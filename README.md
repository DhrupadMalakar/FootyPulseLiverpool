# FootyPulse
### Automated Liverpool FC Matchday Fan Sentiment Engine

FootyPulse is a fully automated matchday analytics system that collects real Reddit comments from Liverpool FC match and post-match threads, processes them through a multi-step NLP pipeline, and generates a clean, professional PDF sentiment report after every game.

This system runs locally, requires no cloud infrastructure, and produces matchday insights in a single command.

---

## 🚀 Features

### **1. Automated Reddit Scraper**
Fetches comments from:
- Match threads  
- Post-match threads  
- High-engagement fan discussions  

Up to **1000 real comments** per matchday are collected using PRAW/Pushshift-style scraping.

### **2. NLP + Embedding Pipeline**
- Cleans comments  
- Generates embeddings using OpenAI's `text-embedding-3-small`  
- Clusters into themes using K-Means  
- Extracts top keywords  
- Identifies player mentions using a **custom nickname map**  
- Separates Liverpool players from opponents (e.g., Doku, Haaland, Foden, etc.)

### **3. GPT-Based Cluster Summaries**
Each cluster is summarized using `gpt-4o-mini` into:
- Emotional mood  
- Key complaints  
- Praises  
- Tactical themes  
- Player-specific discussions  

A final combined **Fanbase Report** is generated automatically.

### **4. Wordcloud Generation**
Two visual outputs:
- **Liverpool player mentions**  
- **Opponent players/managers**  

Generated using matplotlib.

### **5. Corporate-Style PDF Report**
A polished PDF is created using ReportLab with:
- Title page  
- Date  
- Section headings  
- Full fan sentiment report  
- Wordclouds  
- Page numbers  

See `/examples/` for sample outputs.

---

## 🛠 Project Structure

footypulse/
│
├── fetch_match_threads.py # Scrapes Reddit match threads
├── analyze_comments.py # Embeddings, clustering, GPT summaries
├── make_wordclouds.py # Generates text-cloud visualizations
├── make_pdf_report.py # Builds corporate-style PDF report
├── matchday.py # Full automated pipeline
│
├── requirements.txt # Dependencies
└── examples/ # Sample report + wordclouds (optional)

---

## 🔧 Installation

git clone https://github.com/YOUR_USERNAME/FootyPulse.git
cd FootyPulse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

---

## ▶️ Running the Full Pipeline

Simply run:

python matchday.py

This triggers:
1. Reddit scraping  
2. Comment analysis  
3. Cluster generation  
4. GPT summaries  
5. Wordcloud creation  
6. PDF report generation  

The final PDF will be saved as:

liverpool_fan_report.pdf

---

## ⚽ Player Detection Logic (Custom Nickname Map)

FootyPulse uses a manually verified player-nickname mapping for:
- All current Liverpool FC players  
- Common fan-used nicknames (e.g., “Mo”, “VVD”, “Macca”, “Gaks”)  
- Opponent player filtering  

This prevents misclassification (e.g., Doku → City, Trent → Madrid).

---

## 📄 Example Output

See the sample PDF and wordcloud images inside `/examples`.

---

## 📚 Roadmap (v1.1 → v2.0)

- Add match statistics from FBRef  
- Add deep opponent analysis  
- Add match timeline sentiment graph  
- Add player-specific radar charts  
- Deploy a web dashboard version  
- Add automatic posting to LinkedIn/Twitter  
- Upgrade to weekly reports for all PL clubs  

---

## 👤 Author

**Dhrupad Malakar**  
Sports Analytics & Fan Sentiment Analysis  
Open to roles in Football Intelligence, Market Research, or Data Science.

---

## ⭐ License
MIT License.
