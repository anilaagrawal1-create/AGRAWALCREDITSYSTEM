from flask import Flask, render_template, request

app = Flask(__name__)

# -------------------------------
# CREDIT DECISION FUNCTION
# -------------------------------
def credit_decision(cibil, income, emi, enquiries, dpd30, dpd60, dpd90):

    foir = emi / income if income > 0 else 0

    score = (cibil/10) - (foir*50) - (enquiries*2) - (dpd30*10) - (dpd60*20) - (dpd90*30)

    probability = 1/(1+pow(2.718, -( -5 
        + 0.01*(700-cibil) 
        + 3*foir 
        + 0.2*enquiries 
        + 1.5*dpd30 
        + 2.5*dpd60 
        + 3.5*dpd90 )))

    probability_percent = round(probability * 100, 2)

    # -------------------------------
    # ANIL RULES + FOIR CONTROL
    # -------------------------------
    if foir > 0.5:
        decision = "REJECT (FOIR > 50%)"
    elif enquiries > 10 or dpd90 >= 1:
        decision = "REJECT"
    elif probability < 0.3:
        decision = "APPROVE"
    elif probability < 0.6:
        decision = "REVIEW"
    else:
        decision = "REJECT"

    # -------------------------------
    # RISK CATEGORY
    # -------------------------------
    if probability_percent < 30:
        risk = "LOW"
    elif probability_percent < 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return probability_percent, round(score,2), decision, risk, round(foir*100,2)


# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    try:
        if request.method == "POST":
            cibil = float(request.form.get("cibil", 0))
            income = float(request.form.get("income", 0))
            emi = float(request.form.get("emi", 0))
            enquiries = int(request.form.get("enquiries", 0))
            dpd30 = int(request.form.get("dpd30", 0))
            dpd60 = int(request.form.get("dpd60", 0))
            dpd90 = int(request.form.get("dpd90", 0))

            probability, score, decision, risk, foir = credit_decision(
                cibil, income, emi, enquiries, dpd30, dpd60, dpd90
            )

            result = {
                "probability": probability,
                "score": score,
                "decision": decision,
                "risk": risk,
                "foir": foir
            }

    except Exception as e:
        # Show error instead of crashing
        result = {
            "decision": "ERROR",
            "score": "-",
            "probability": "-",
            "risk": "-",
            "foir": "-",
            "error": str(e)
        }

    return render_template("index.html", result=result)


# -------------------------------
# RUN APP (LOCAL + RENDER SAFE)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)