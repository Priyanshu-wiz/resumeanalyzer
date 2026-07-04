from flask import Flask,render_template,redirect,session,request
from db import Base,engine,Sessionlocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
app=Flask("__name__")

Base.metadata.create_all(bind=engine)
@app.route('/')
def home():
    if "user" in session:
        return redirect("/dashboard.html")
    else:
        return redirect("login.html")
@app.route('/signup',methods=["GET","POST"])
def signup():
    db=Sessionlocal()
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        existing_user=db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "user already exists"
        user=models.User(email=email,password=password)
        db.add(user)
        db.commit()
        return redirect("/login.html")
    return render_template("/signup.html")
    
@app.route('/login')
def login():
    db=Sessionlocal()
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        user=db.query(models.User).filter_by(email=email,password=password).first()
        if user:
            session["user"]=user.email
            return redirect ("/dashboard.html")
        else:
            return " invalid credientials"

    return render_template("/login.html")
@app.route('/dashboard.html',method=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect('/login.html')
    result=None
    if request.method=="POST":
        user_goal=request.form.get("role")
        resume_text=request.form.get("resumetxt")

        file=request.file.get("file")

        if file and file.name !="":
            if file.filename.endswith(".pdf"):
                try:
                    text=""
                    readpdf=PyPDF2.PdfReader(file)
                    for page in readpdf.pages:
                        text += page.extract_text() or ""
                    resume_text=text
                except Exception as e:
                    result={"error": f"pdf error: {str(e)}"}

            elif file.filename.endswith(".docx"):
                try:
                    text=""
                    readdocx=docx.document(file)
                    for para in readdocx.paragraphs:
                        text+=para.text +"\n"
                    resume_text=text
                except Exception as e:
                    result={"error": f"docx error: {str(e)}"}

    if resume_text and user_goal:
        try:
            result=analyze_resume(resume_text,user_goal)
            db= Sessionlocal()
            user =db.query(models.User).filter_by(email=session["user"]).first()
            report=models.Report(
                user_id=user.id,
                resume_text=resume_text,
                results=json.dump(result)
            )
            db.add(report)
            db.commit()
            
        except Exception as e:
            result={"error":f"Ai error"}
    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )





            

if __name__=="__main__":
    app.run(debug=True)