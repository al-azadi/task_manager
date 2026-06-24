import customtkinter as ctk
import sqlite3


db = sqlite3.connect("tasks.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT,
    priority TEXT, status TEXT)""")
db.commit()


THEMES = {
    "dark": {
        "bg": "#0a0a0f", "card": "#1d1d4c", "input": "#2F2FA5",
        "border": "#2a2a3e", "text": "#f1f5f9", "muted": "#64748b",
        "accent": "#6366f1", "ok": "#10b981", "del": "#ef4444", "warn": "#f59e0b"
    },
    "light": {
        "bg": "#f8fafc", "card": "#ffffff", "input": "#f1f5f9",
        "border": "#cbd5e1", "text": "#1e293b", "muted": "#94a3b8",
        "accent": "#4f46e5", "ok": "#059669", "del": "#dc2626", "warn": "#d97706"
    }
}
PRIORITY = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}

current_theme = "dark"
C = THEMES[current_theme]

def switch_theme(mode):
    global current_theme, C
    theme_key = "dark" if mode == "system" else mode 
    current_theme = theme_key
    C = THEMES[theme_key]
    ctk.set_appearance_mode(mode)
    rebuild_ui()


def add():
    t, d, p = title.get().strip(), desc.get("1.0","end").strip(), prio.get()
    if not t: return
    cursor.execute("INSERT INTO tasks VALUES(NULL,?,?,?,?)", (t,d,p,"Pending"))
    db.commit(); title.delete(0,"end"); desc.delete("1.0","end"); load()

def load(search_term="", status_filter="All"):
    for w in frame.winfo_children(): w.destroy()

    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search_term:
        sql += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    if status_filter != "All":
        sql += " AND status = ?"
        params.append(status_filter)
    
    sql += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"
    
    cursor.execute(sql, params)
    tasks = cursor.fetchall()
    
    if not tasks:
        msg = "📭 No tasks yet"
        if search_term and status_filter != "All":
            msg = f'🔍 No {status_filter} tasks match "{search_term}"'
        elif search_term:
            msg = f'🔍 No results for "{search_term}"'
        elif status_filter != "All":
            msg = f'📭 No {status_filter} tasks'
        ctk.CTkLabel(frame, text=msg, font=("Arial",18), text_color=C["muted"]).pack(pady=50)
        return
    for t in tasks: card(t)

def search():
    term = search_entry.get().strip()
    status = status_filter.get()
    load(term, status)

def clear_search():
    search_entry.delete(0, "end")
    status_filter.set("All")
    load()

def view_all():
    search_entry.delete(0, "end")
    status_filter.set("All")
    load()

def filter_status(status):
    status_filter.set(status)
    term = search_entry.get().strip()
    load(term, status)
def delete(i):
    cursor.execute("DELETE FROM tasks WHERE id=?", (i,)); db.commit(); load()

def done(i):
    cursor.execute("UPDATE tasks SET status='Done' WHERE id=?", (i,)); db.commit(); load()

def edit(i, t, d, p, s):
    win = ctk.CTkToplevel(app); win.title("Edit"); win.geometry("400x420")
    win.configure(fg_color=C["bg"]); win.grab_set(); win.resizable(False,False)
    ctk.CTkLabel(win, text="✏️ Edit Task", font=("Arial",20,"bold"), text_color=C["accent"]).pack(pady=15)
    et = ctk.CTkEntry(win, width=350, fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    et.insert(0,t); et.pack(pady=5)
    ed = ctk.CTkTextbox(win, width=350, height=80, fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    ed.insert("1.0",d); ed.pack(pady=5)
    ep = ctk.CTkComboBox(win, values=["High","Medium","Low"], width=150); ep.set(p); ep.pack(pady=5)
    es = ctk.CTkComboBox(win, values=["Pending","Done"], width=150); es.set(s); es.pack(pady=5)
    def save():
        cursor.execute("UPDATE tasks SET title=?,description=?,priority=?,status=? WHERE id=?",
            (et.get().strip(), ed.get("1.0","end").strip(), ep.get(), es.get(), i))
        db.commit(); win.destroy(); load()
    ctk.CTkButton(win, text="💾 Save", fg_color=C["accent"], command=save).pack(pady=15)

def card(task):
    i,t,d,p,s = task
    done = s=="Done"
    c = ctk.CTkFrame(frame, fg_color="#e8f5e9" if (done and current_theme=="light") else ("#0f1f17" if done else C["card"]),
                     corner_radius=12, border_width=1, border_color=C["border"])
    c.pack(padx=10, pady=6, fill="x")
    ctk.CTkFrame(c, fg_color=PRIORITY.get(p,C["muted"]), width=4, corner_radius=2).pack(side="left", fill="y", pady=4)
    content = ctk.CTkFrame(c, fg_color="transparent"); content.pack(side="left", fill="both", expand=True, padx=15, pady=12)
    row = ctk.CTkFrame(content, fg_color="transparent"); row.pack(fill="x")
    ctk.CTkLabel(row, text=f"{'✅' if done else '📌'} {t}", font=("Arial",15,"bold"),
                text_color=C["ok"] if done else C["text"]).pack(side="left")
    ctk.CTkLabel(row, text=f"  {s}  ", font=("Arial",10,"bold"), text_color="white",
                 fg_color=C["ok"] if done else C["warn"], corner_radius=10).pack(side="right")
    if d: ctk.CTkLabel(content, text=d[:100]+("..." if len(d)>100 else ""), font=("Arial",12),
                       text_color=C["muted"], wraplength=400).pack(anchor="w", pady=5)
    ctk.CTkLabel(content, text=f"🔥 {p}", font=("Arial",11,"bold"), text_color=PRIORITY.get(p)).pack(anchor="w")
    btns = ctk.CTkFrame(c, fg_color="transparent", width=90); btns.pack(side="right", padx=10, pady=10); btns.pack_propagate(False)
    ctk.CTkButton(btns, text="✏️ edit", width=32, height=32, fg_color=C["accent"], command=lambda: edit(i,t,d,p,s)).pack(pady=2)
    if not done: ctk.CTkButton(btns, text="✓", width=32, height=32, fg_color=C["ok"], command=lambda: done(i)).pack(pady=2)
    ctk.CTkButton(btns, text="🗑 del", width=32, height=32, fg_color=C["del"], command=lambda: delete(i)).pack(pady=2)


def rebuild_ui():
    global title, desc, prio, frame, search_entry, status_filter
    for w in app.winfo_children(): w.destroy()
    
    
    head = ctk.CTkFrame(app, fg_color="transparent"); head.pack(fill="x", padx=20, pady=15)
    ctk.CTkLabel(head, text="🚀 TaskFlow", font=("Arial",28,"bold"), text_color=C["accent"]).pack(side="left")
    
    
    theme_frame = ctk.CTkFrame(head, fg_color="transparent"); theme_frame.pack(side="right")
    for mode, icon in [("dark","🌙"), ("light","☀️"), ("system","💻")]:
        ctk.CTkButton(theme_frame, text=icon, width=36, height=36, corner_radius=18,
                    fg_color=C["accent"] if current_theme==("dark" if mode=="system" else mode) else C["card"],
                    command=lambda m=mode: switch_theme(m)).pack(side="left", padx=3)

    search_frame = ctk.CTkFrame(app, fg_color=C["card"], corner_radius=16)
    search_frame.pack(padx=20, pady=(0,10), fill="x")
    search_inner = ctk.CTkFrame(search_frame, fg_color="transparent")
    search_inner.pack(padx=20, pady=15, fill="x")
    
    search_entry = ctk.CTkEntry(search_inner, width=250, height=40, 
                                fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    search_entry.pack(side="left", padx=(0,10))
    
    status_filter = ctk.CTkComboBox(search_inner, values=["All","Pending","Done"], width=120, height=40,
                                    fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    status_filter.set("All")
    status_filter.pack(side="left", padx=(0,10))
    
    ctk.CTkButton(search_inner, text="🔍 Search", width=90, height=40, 
                  fg_color=C["accent"], command=search).pack(side="left", padx=(0,5))
    ctk.CTkButton(search_inner, text="✕ Clear", width=80, height=40, 
                  fg_color=C["del"], command=clear_search).pack(side="left", padx=(0,5))
    ctk.CTkButton(search_inner, text="📋 View All", width=90, height=40, 
                  fg_color=C["ok"], command=view_all).pack(side="left")

    quick_frame = ctk.CTkFrame(app, fg_color="transparent")
    quick_frame.pack(padx=20, pady=(0,5), fill="x")
    
    ctk.CTkButton(quick_frame, text="⏳ Pending", width=100, height=32,
                  fg_color=C["warn"], command=lambda: filter_status("Pending")).pack(side="left", padx=(0,5))
    ctk.CTkButton(quick_frame, text="✅ Done", width=100, height=32,
                  fg_color=C["ok"], command=lambda: filter_status("Done")).pack(side="left", padx=(0,5))
    ctk.CTkButton(quick_frame, text="📋 View All", width=100, height=32,
                  fg_color=C["accent"], command=view_all).pack(side="left")
    
    inp = ctk.CTkFrame(app, fg_color=C["card"], corner_radius=16); inp.pack(padx=20, pady=10, fill="x")
    inner = ctk.CTkFrame(inp, fg_color="transparent"); inner.pack(padx=20, pady=20)
    title = ctk.CTkEntry(inner, width=400, height=40, placeholder_text="Title...", fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    title.pack(pady=5)
    desc = ctk.CTkTextbox(inner, width=400, height=60, fg_color=C["input"], border_color=C["border"], text_color=C["text"])
    desc.insert("1.0", "Description..."); desc.pack(pady=5)
    row = ctk.CTkFrame(inner, fg_color="transparent"); row.pack(fill="x", pady=5)
    prio = ctk.CTkComboBox(row, values=["High","Medium","Low"], width=150); prio.set("Medium"); prio.pack(side="left")
    ctk.CTkButton(row, text="➕ Add", width=100, fg_color=C["accent"], command=add).pack(side="right")

    
    container = ctk.CTkFrame(app, fg_color="transparent"); container.pack(padx=20, pady=10, fill="both", expand=True)
    canvas = ctk.CTkCanvas(container, bg=C["bg"], highlightthickness=0); canvas.pack(side="left", fill="both", expand=True)
    scroll = ctk.CTkScrollbar(container, command=canvas.yview); scroll.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scroll.set)
    frame = ctk.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window((0,0), window=frame, anchor="nw", width=610)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/120), "units"))
    
    load()


ctk.set_appearance_mode("dark")
app = ctk.CTk(); app.title("TaskFlow"); app.geometry("650x800")
rebuild_ui()
app.mainloop()
db.close()