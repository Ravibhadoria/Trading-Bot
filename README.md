
# Delta Trading Bot 💹


**Delta Trading Bot** is a professional Python desktop application designed for simulating BTC options trading on Delta Exchange. It combines **automated trading**, **manual trade placement**, **dynamic trailing stop-loss**, and **real-time analytics** in a clean and intuitive Tkinter GUI.  

This project demonstrates robust trading logic, multi-threaded GUI updates, and practical risk management strategies. Perfect for learning algorithmic trading concepts and building a strong portfolio in Python and financial tech.  

---

## 🌟 Key Features

- **Automated Trading**
  - Executes **CALL** trades when RSI > 60 and **PUT** trades when RSI < 40.  
  - Limits: max 3 active trades and 10 trades per day for safe simulation.  
- **Manual Trading**
  - Place **Bull (CALL)** or **Bear (PUT)** trades instantly via GUI.  
- **Trailing Stop-Loss**
  - Adjusts stop-loss dynamically based on market movements.  
- **Real-Time Analytics**
  - Monitors BTC price, account balance, P&L, active trades, and daily trades count.  
- **Live Logs & Status Updates**
  - Provides actionable insights via info, warning, and error messages.  
- **Full Bot Control**
  - Start, Pause/Resume, Stop, and Reset for complete flexibility.  

---

## ![WhatsApp Image 2025-09-25 at 19 16 57_248d527f](https://github.com/user-attachments/assets/6b73d15a-768e-47cb-870a-50f0c48529c4)




## ⚙️ Installation (Quick Start)

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/delta-trading-bot.git
cd delta-trading-bot
````

2. **Create and activate a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

> Required library: `requests` (Tkinter is included with Python).

---

## 🖥 Usage

Run the application:

```bash
trading-bot.py  
```

**Workflow for Success:**

1. Configure trading parameters: **Expiry Date, Lots, Amount, Stop-Loss %**.
2. Start **manual trades** using Bull or Bear buttons.
3. Automated trading will execute trades based on RSI strategy.
4. Track **real-time balance, P&L, and trades** in the dashboard.
5. Control the bot using **Pause**, **Stop**, and **Reset** buttons.

---

## 📊 Project Structure

```
delta-trading-bot/
│
├─ main.py               # Tkinter GUI application
├─ trading_bot.py        # TradingBot class & trading logic
├─ requirements.txt      # Python dependencies
├─ README.md             # Project documentation
└─ assets/               # Screenshots, icons, demo images
```

---

## 🛠 Technical Overview

* **Multi-threaded GUI:** Thread-safe queue updates for smooth performance.
* **Automated Trading Logic:** Evaluates RSI thresholds and executes trades safely.
* **Trailing Stop-Loss Management:** Ensures risk control for each trade.
* **Real-Time P&L Tracking:** Updates profit/loss continuously for actionable insights.
* **Extensible Architecture:** Modular design for easy upgrades and API integration.

---

## 🎯 Future Enhancements

* Integrate **live trading via Delta Exchange API**.
* Add **multi-currency support** for crypto trading.
* Implement **advanced technical indicators** like MACD, Bollinger Bands.
* Add **analytics dashboards** and **performance reporting**.
* Enhance **GUI** with interactive charts and trade visualizations.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🤝 Contributing

Contributions are warmly welcome! Please open issues or submit pull requests for:

* Bug fixes
* Feature requests
* Code improvements
* Documentation enhancements

**Positive Collaboration:** This project encourages learning, experimentation, and growth in algorithmic trading and Python development.

---

### 💡 Why This Project?

* Demonstrates real-world **algorithmic trading strategies**.
* Showcases **Python GUI development** with Tkinter.
* Highlights **risk management** and **threaded programming**.
* Ideal for **portfolio, GitHub showcase, and professional presentation**.

