import tkinter as tk
from tkinter import ttk
import sqlite3


# DATABASE
db = sqlite3.connect("tasks.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
description TEXT,
priority TEXT,
status TEXT)
""")
db.commit()

dark = {
"bg":"#0a0a0f","card":"#1d1d4c","input":"#2F2FA5",
"text":"#f1f5f9","accent":"#6366f1",
"ok":"#10b981","del":"#ef4444","warn":"#f59e0b"
}

light = {
"bg":"#f8fafc","card":"#ffffff","input":"#eeeeee",
"text":"#222222","accent":"#4f46e5",
"ok":"#059669","del":"#dc2626","warn":"#d97706"
}

C = dark
priority_color={
"High":"#ef4444",
"Medium":"#f59e0b",
"Low":"#10b981"
}


def add():
    t=title.get().strip()
    d=desc.get("1.0","end").strip()
    
    if t:
        cur.execute(
        "INSERT INTO tasks VALUES(NULL,?,?,?,?)",
        (t,d,prio.get(),"Pending"))
        db.commit()
        title.delete(0,"end")
        desc.delete("1.0","end")
        load()


def load(search="",status="All"):

    for x in frame.winfo_children():
        x.destroy()

    sql="SELECT * FROM tasks WHERE 1=1"
    data=[]

    if search:
        sql+=" AND(title LIKE ? OR description LIKE ?)"
        data += [f"%{search}%",f"%{search}%"]

    if status!="All":
        sql+=" AND status=?"
        data.append(status)

    sql+=" ORDER BY id DESC"

    cur.execute(sql,data)

    for task in cur.fetchall():
        create_card(task)


def search():
    load(search_box.get(),filter_box.get())


def clear():
    search_box.delete(0,"end")
    filter_box.set("All")
    load()


def delete(i):
    cur.execute("DELETE FROM tasks WHERE id=?",(i,))
    db.commit()
    load()


def done(i):
    cur.execute(
    "UPDATE tasks SET status='Done' WHERE id=?",
    (i,))
    db.commit()
    load()


def edit(task):

    win=tk.Toplevel(app)
    win.geometry("350x350")
    win.title("Edit")

    t=tk.Entry(win,width=35)
    t.insert(0,task[1])
    t.pack(pady=5)


    d=tk.Text(win,width=35,height=5)
    d.insert("1.0",task[2])
    d.pack(pady=5)


    p=ttk.Combobox(
    win,
    values=["High","Medium","Low"])
    p.set(task[3])
    p.pack()


    s=ttk.Combobox(
    win,
    values=["Pending","Done"])
    s.set(task[4])
    s.pack()


    def save():
     cur.execute("""
        UPDATE tasks SET
        title=?,
        description=?,
        priority=?,
        status=?
        WHERE id=?
        """,
        (
        t.get(),
        d.get("1.0","end"),
        p.get(),
        s.get(),
        task[0]
        ))

    db.commit()
    win.destroy()
    load()


    tk.Button(
    win,
    text="Save",
    command=save).pack(pady=10)


def create_card(task):

    box=tk.Frame(
    frame,
    bg=C["card"],
    bd=2,
    relief="groove")

    box.pack(
    fill="x",
    padx=10,
    pady=5)

    tk.Label(
    box,
    text=("✅ " if task[4]=="Done" else "📌 ")+task[1],
    bg=C["card"],
    fg=C["text"],
    font=("Arial",14,"bold")
    ).pack(anchor="w")

    tk.Label(
    box,
    text=task[2],
    bg=C["card"],
    fg="gray"
    ).pack(anchor="w")



    tk.Label(
    box,
    text="🔥 "+task[3],
    bg=C["card"],
    fg=priority_color[task[3]]
    ).pack(anchor="w")



    btn=tk.Frame(box,bg=C["card"])
    btn.pack()


    tk.Button(
    btn,
    text="Edit",
    command=lambda:edit(task)
    ).pack(side="left")


    if task[4]!="Done":
        tk.Button(
        btn,
        text="Done",
        command=lambda:done(task[0])
        ).pack(side="left")


    tk.Button(
    btn,
    text="Delete",
    command=lambda:delete(task[0])
    ).pack(side="left")




# THEME
def theme():
    global C
    C = light if C==dark else dark
    rebuild()



# UI
def rebuild():

    global title,desc,prio,frame
    global search_box,filter_box


    for x in app.winfo_children():
        x.destroy()

    app.configure(bg=C["bg"])

    tk.Button(
    app,
    text="🌙 / ☀️",
    command=theme
    ).pack()

    tk.Label(
    app,
    text="🚀 TO-DO LIST",
    font=("Arial",25,"bold"),
    bg=C["bg"],
    fg=C["del"]
    ).pack()

    search_box=tk.Entry(app)
    search_box.pack(pady=5)


    filter_box=ttk.Combobox(
    app,
    values=["All","Pending","Done"])
    filter_box.set("All")
    filter_box.pack()

    tk.Button(
    app,
    text="Search",
    command=search
    ).pack()

    tk.Button(
    app,
    text="Clear",
    command=clear
    ).pack()


    title=tk.Entry(app,width=40)
    title.pack(pady=5)


    desc=tk.Text(
    app,
    width=40,
    height=4)
    desc.pack()


    prio=ttk.Combobox(
    app,
    values=["High","Medium","Low"])
    prio.set("Medium")
    prio.pack()



    tk.Button(
    app,
    text="➕ Add",
    command=add
    ).pack(pady=5)



    canvas=tk.Canvas(
    app,
    bg=C["bg"])

    canvas.pack(
    fill="both",
    expand=True)


    global frame

    frame=tk.Frame(
    canvas,
    bg=C["bg"])

    canvas.create_window(
    (0,0),
    window=frame,
    anchor="nw")


    frame.bind(
    "<Configure>",
    lambda e:
    canvas.configure(
    scrollregion=canvas.bbox("all")))

    load()


app=tk.Tk()
app.title("TO DO LIST")
app.geometry("650x800")

rebuild()

app.mainloop()

db.close()