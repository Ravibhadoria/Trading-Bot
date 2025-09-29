#4 
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
from datetime import datetime
import random
import requests
import time

# --- Configuration & Strategy Parameters ---
RSI_UPPER_BAND = 60
RSI_LOWER_BAND = 40
CURRENCY = "BTC"


class TradingBot:
    def __init__(self, gui_queue, get_gui_inputs):
        self.is_running = False
        self.is_paused = False
        self.gui_queue = gui_queue
        self.get_gui_inputs = get_gui_inputs
        self.active_trades = []
        self.trades_today_count = 0
        self.current_price = 0
        self.balance = 0.00
        self.pnl = 0.00
        self.initial_balance = 0.00

    def log_message(self, msg_type, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.gui_queue.put({'type': 'log', 'data': f"[{timestamp}] {message}", 'log_type': msg_type})

    def get_spot_price(self):
        """Fetch BTC price from API"""
        try:
            response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = float(data['data']['rates']['USD'])
                return price
        except:
            pass
        return self.current_price or 50000

    def update_gui_data(self, price):
        self.gui_queue.put({'type': 'price_update', 'data': {
            'price': price,
            'balance': self.balance,
            'pnl': self.pnl,
            'trades_count': self.trades_today_count
        }})
        self.gui_queue.put({'type': 'update_trades', 'data': self.active_trades})

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.log_message('info', "Trading bot initialized")
            threading.Thread(target=self.run_strategy_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.is_paused = False

    def pause(self):
        self.is_paused = not self.is_paused

    def reset(self):
        self.stop()
        self.active_trades = []
        self.trades_today_count = 0
        self.balance = self.initial_balance
        self.pnl = 0.00
        self.update_gui_data(self.current_price or 50000)

    def run_strategy_loop(self):
        while self.is_running:
            if not self.is_paused:
                inputs = self.get_gui_inputs()
                spot_price = self.get_spot_price()
                self.current_price = spot_price
                self.update_gui_data(spot_price)

                # Simulate trades automatically for demo
                if len(self.active_trades) < 3 and self.trades_today_count < 10:
                    rsi = random.uniform(20, 80)
                    if rsi > RSI_UPPER_BAND:
                        self.place_trade('CALL', inputs)
                    elif rsi < RSI_LOWER_BAND:
                        self.place_trade('PUT', inputs)

                # Update P&L and trailing stop-loss
                for trade in list(self.active_trades):
                    if trade['status'] != 'OPEN':
                        continue

                    if trade['type'] == 'CALL':
                        trade['current_pnl'] = (spot_price - trade['entry_price']) * trade['lots']
                        # Trailing SL: move SL up if price goes up
                        if spot_price > trade['highest_price']:
                            trade['highest_price'] = spot_price
                            trade['stop_loss_price'] = max(
                                trade['stop_loss_price'],
                                spot_price * (1 - trade['sl_percent'] / 100)
                            )
                        # Check SL hit
                        if spot_price <= trade['stop_loss_price']:
                            trade['status'] = 'CLOSED (SL)'
                            self.log_message('warning', f"CALL trade hit stop-loss at ${spot_price:.2f} and was closed")

                    else:  # PUT
                        trade['current_pnl'] = (trade['entry_price'] - spot_price) * trade['lots']
                        # Trailing SL: move SL down if price goes down
                        if spot_price < trade['lowest_price']:
                            trade['lowest_price'] = spot_price
                            trade['stop_loss_price'] = min(
                                trade['stop_loss_price'],
                                spot_price * (1 + trade['sl_percent'] / 100)
                            )
                        # Check SL hit
                        if spot_price >= trade['stop_loss_price']:
                            trade['status'] = 'CLOSED (SL)'
                            self.log_message('warning', f"PUT trade hit stop-loss at ${spot_price:.2f} and was closed")

            time.sleep(10)

    def place_trade(self, trade_type, inputs):
        spot_price = self.get_spot_price()
        lots = float(inputs.get('lots', 1))
        if inputs.get('amount'):
            lots = float(inputs['amount']) / spot_price

        sl_percent = inputs.get('stop_loss_percent', 2.0)

        strike_base = round(spot_price / 100) * 100
        strike = strike_base + random.choice([-100, 0, 100])

        stop_loss_price = spot_price * (1 - sl_percent / 100) if trade_type == 'CALL' else spot_price * (1 + sl_percent / 100)

        trade = {
            'symbol': f'BTC-{strike}-{"CE" if trade_type=="CALL" else "PE"}',
            'type': trade_type,
            'strike': strike,
            'entry_price': spot_price,
            'highest_price': spot_price,
            'lowest_price': spot_price,
            'stop_loss_price': stop_loss_price,
            'sl_percent': sl_percent,
            'current_pnl': 0,
            'lots': lots,
            'status': 'OPEN'
        }

        self.active_trades.append(trade)
        self.trades_today_count += 1
        self.log_message('info', f"{trade_type} trade placed at ${spot_price:,.2f} with {lots:.4f} lots | SL: {sl_percent}%")
        self.update_gui_data(spot_price)


class DeltaTradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Delta Exchange BTC Options Trading Bot")
        self.geometry("950x650")
        self.configure(bg='#f5f5f5')
        self.resizable(True, True)

        self.gui_queue = queue.Queue()
        self.bot = TradingBot(self.gui_queue, self.get_gui_inputs)

        # Variables
        self.currency_var = tk.StringVar(value="BTC")
        self.price_var = tk.StringVar(value="Loading...")
        self.balance_var = tk.StringVar(value="$0.00")
        self.expiry_var = tk.StringVar(value="24-09-2025")
        self.lots_var = tk.StringVar(value="1")
        self.amount_var = tk.StringVar(value="")
        self.trades_today_var = tk.StringVar(value="0")
        self.delta_var = tk.StringVar(value="N/A")
        self.pnl_var = tk.StringVar(value="$0.00")
        self.sl_percent_var = tk.StringVar(value="2.0")

        self.setup_styles()
        self.create_widgets()
        self.process_gui_queue()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Action.TButton', font=('Segoe UI', 10), padding=(10, 6))

    def get_gui_inputs(self):
        lots = self.lots_var.get()
        amount = self.amount_var.get()
        sl_percent = self.sl_percent_var.get()
        return {
            'lots': float(lots) if lots else None,
            'amount': float(amount) if amount else None,
            'expiry': self.expiry_var.get(),
            'stop_loss_percent': float(sl_percent) if sl_percent else 2.0
        }

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Trading Parameters ---
        params_frame = ttk.LabelFrame(main_frame, text="Trading Parameters", padding=10)
        params_frame.grid(row=0, column=0, sticky='ew', pady=5)
        main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(params_frame, text="Currency:").grid(row=0, column=0, sticky='w')
        ttk.Label(params_frame, textvariable=self.currency_var, font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(params_frame, text="Price:").grid(row=0, column=2, sticky='w')
        self.price_label = ttk.Label(params_frame, textvariable=self.price_var, font=('Segoe UI', 9, 'bold'))
        self.price_label.grid(row=0, column=3, sticky='w', padx=5)

        ttk.Label(params_frame, text="Balance:").grid(row=0, column=4, sticky='w')
        ttk.Label(params_frame, textvariable=self.balance_var, font=('Segoe UI', 9, 'bold')).grid(row=0, column=5, sticky='w', padx=5)

        # Row 2 - Inputs
        ttk.Label(params_frame, text="Expiry Date:").grid(row=1, column=0, sticky='w', pady=5)
        expiry_combo = ttk.Combobox(params_frame, textvariable=self.expiry_var, state='readonly', width=12)
        expiry_combo['values'] = ["24-09-2025", "25-09-2025", "30-09-2025"]
        expiry_combo.grid(row=1, column=1, sticky='w', pady=5)

        ttk.Label(params_frame, text="Lots:").grid(row=1, column=2, sticky='w')
        ttk.Entry(params_frame, textvariable=self.lots_var, width=10).grid(row=1, column=3, sticky='w')

        ttk.Label(params_frame, text="Amount ($):").grid(row=1, column=4, sticky='w')
        ttk.Entry(params_frame, textvariable=self.amount_var, width=12).grid(row=1, column=5, sticky='w')

        ttk.Label(params_frame, text="Trades Today:").grid(row=1, column=6, sticky='w')
        ttk.Label(params_frame, textvariable=self.trades_today_var, font=('Segoe UI', 9, 'bold')).grid(row=1, column=7, sticky='w')

        # Row 3 - P&L and Delta + SL
        ttk.Label(params_frame, text="Delta:").grid(row=2, column=0, sticky='w')
        ttk.Label(params_frame, textvariable=self.delta_var, font=('Segoe UI', 9, 'bold')).grid(row=2, column=1, sticky='w', padx=5)
        ttk.Label(params_frame, text="P&L:").grid(row=2, column=2, sticky='w')
        ttk.Label(params_frame, textvariable=self.pnl_var, font=('Segoe UI', 9, 'bold')).grid(row=2, column=3, sticky='w', padx=5)

        ttk.Label(params_frame, text="Stop-Loss %:").grid(row=2, column=4, sticky='w')
        ttk.Entry(params_frame, textvariable=self.sl_percent_var, width=10).grid(row=2, column=5, sticky='w')

        # --- Control Buttons ---
        button_frame = ttk.Frame(params_frame)
        button_frame.grid(row=3, column=0, columnspan=8, pady=10, sticky='w')

        self.bull_button = ttk.Button(button_frame, text="Bull 1", style='Action.TButton', width=12,
                                      command=lambda: self.place_manual_trade('CALL'))
        self.bull_button.pack(side='left', padx=5)
        self.bear_button = ttk.Button(button_frame, text="Bear 1", style='Action.TButton', width=12,
                                      command=lambda: self.place_manual_trade('PUT'))
        self.bear_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(button_frame, text="Stop", style='Action.TButton', width=12,
                                      command=self.stop_bot, state='disabled')
        self.stop_button.pack(side='left', padx=20)
        self.pause_button = ttk.Button(button_frame, text="Pause", style='Action.TButton', width=12,
                                       command=self.pause_bot, state='disabled')
        self.pause_button.pack(side='left', padx=5)
        self.reset_button = ttk.Button(button_frame, text="Reset", style='Action.TButton', width=12,
                                       command=self.reset_bot)
        self.reset_button.pack(side='left', padx=5)

        # --- Trades Table ---
        trades_frame = ttk.LabelFrame(main_frame, text="Current Trades", padding=10)
        trades_frame.grid(row=1, column=0, sticky='nsew', pady=5)
        main_frame.grid_rowconfigure(1, weight=1)

        columns = ('Symbol', 'Type', 'Strike', 'Entry Price', 'Stop-Loss', 'Current P&L', 'Status')
        self.trades_tree = ttk.Treeview(trades_frame, columns=columns, show='headings', height=10)
        self.trades_tree.grid(row=0, column=0, sticky='nsew')
        trades_frame.grid_rowconfigure(0, weight=1)
        trades_frame.grid_columnconfigure(0, weight=1)

        for col in columns:
            self.trades_tree.heading(col, text=col)
            self.trades_tree.column(col, width=120)

        trades_scrollbar = ttk.Scrollbar(trades_frame, orient='vertical', command=self.trades_tree.yview)
        trades_scrollbar.grid(row=0, column=1, sticky='ns')
        self.trades_tree.configure(yscrollcommand=trades_scrollbar.set)

        # --- Logs ---
        logs_frame = ttk.LabelFrame(main_frame, text="Status & Logs", padding=10)
        logs_frame.grid(row=2, column=0, sticky='nsew')
        main_frame.grid_rowconfigure(2, weight=1)

        self.log_text = scrolledtext.ScrolledText(logs_frame, height=12, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky='nsew')
        logs_frame.grid_rowconfigure(0, weight=1)
        logs_frame.grid_columnconfigure(0, weight=1)

        self.log_text.tag_config('warning', foreground='#FF8C00')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('info', foreground='blue')
        self.log_text.tag_config('success', foreground='green')

    # --- Button actions ---
    def place_manual_trade(self, trade_type):
        if not self.bot.is_running:
            self.bot.start()
        inputs = self.get_gui_inputs()
        self.bot.place_trade(trade_type, inputs)
        self.stop_button.config(state='normal')
        self.pause_button.config(state='normal')

    def stop_bot(self):
        self.bot.stop()
        self.stop_button.config(state='disabled')
        self.pause_button.config(state='disabled', text='Pause')

    def pause_bot(self):
        self.bot.pause()
        if self.bot.is_paused:
            self.pause_button.config(text='Resume')
        else:
            self.pause_button.config(text='Pause')

    def reset_bot(self):
        if messagebox.askyesno("Reset Confirmation", "Reset all trading data?"):
            self.bot.reset()
            for item in self.trades_tree.get_children():
                self.trades_tree.delete(item)
            self.stop_button.config(state='disabled')
            self.pause_button.config(state='disabled', text='Pause')

    def process_gui_queue(self):
        try:
            while True:
                msg = self.gui_queue.get_nowait()
                if msg['type'] == 'log':
                    self.log_text.insert('end', msg['data'] + '\n', msg.get('log_type', 'info'))
                    self.log_text.see('end')
                elif msg['type'] == 'price_update':
                    self.price_var.set(f"${msg['data']['price']:,.2f}")
                    self.balance_var.set(f"${msg['data']['balance']:.2f}")
                    self.pnl_var.set(f"${msg['data']['pnl']:.2f}")
                    self.trades_today_var.set(str(msg['data']['trades_count']))
                elif msg['type'] == 'update_trades':
                    for item in self.trades_tree.get_children():
                        self.trades_tree.delete(item)
                    for trade in msg['data']:
                        pnl_display = f"${trade['current_pnl']:,.2f}"
                        sl_display = f"${trade['stop_loss_price']:,.2f}"
                        self.trades_tree.insert('', 'end', values=(
                            trade['symbol'], trade['type'], f"${trade['strike']}",
                            f"${trade['entry_price']:,.2f}", sl_display, pnl_display, trade['status']
                        ))
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_gui_queue)


if __name__ == "__main__":
    app = DeltaTradingApp()
    app.mainloop()

