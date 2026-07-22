from flask import Flask,render_template,redirect,session,request
from db import Base,engine,Sessionlocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
app=Flask("__name__")
app.secret_key="seceretkey"  # Replace

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    app.logger.warning("Database tables could not be created automatically: %s", exc)

@app.route('/')
def home():
    if "user" in session:
        return redirect("/dashboard.html")
    else:
        return redirect("/login.html")

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("signup.html", error="Email and password are required")

        try:
            db = Sessionlocal()
            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return render_template("signup.html", error="User already exists")

            user = models.User(email=email, password=password)
            db.add(user)
            db.commit()
            return redirect("/login.html")
        except Exception as exc:
            db.rollback()
            app.logger.exception("Signup failed")
            return render_template("signup.html", error="Signup failed. Please try again.")

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
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

    return render_template("login.html")

@app.route('/dashboard.html', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login.html')

    result = None
    resume_text = None
    user_goal = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resumetxt")

        file=request.files.get("file")

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
            result = analyze_resume(resume_text, user_goal)
        except Exception as e:
            app.logger.exception("AI analysis failed")
            result = {"error": f"Ai error: {str(e)}"}

        if isinstance(result, dict) and not result.get("error"):
            try:
                db = Sessionlocal()
                user = db.query(models.User).filter_by(email=session["user"]).first()
                if user is not None:
                    report = models.Report(
                        user_id=user.id,
                        report=resume_text,
                        result=json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
            except Exception as e:
                app.logger.exception("Saving report failed")
    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )

@app.route("/history")
@app.route("/history.html")
def history():
    if "user" not in session:
        return redirect('/login.html')

    db = Sessionlocal()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()
        if user is None:
            return redirect('/login.html')

        reports = (
            db.query(models.Report)
            .filter_by(user_id=user.id)
            .order_by(models.Report.id.desc())
            .all()
        )

        history_items = []
        for report in reports:
            parsed_result = {}
            try:
                parsed_result = json.loads(report.result) if report.result else {}
            except Exception:
                parsed_result = {}

            history_items.append({
                "id": report.id,
                "resume_text": report.report or "",
                "result": parsed_result
            })

        return render_template("history.html", reports=history_items)
    finally:
        db.close()



            

if __name__=="__main__":
    app.run(debug=True)