from flask import Flask, render_template, request

# IMPORTANT: explicitly define template folder
app = Flask(__name__, template_folder="templates")


# -------------------------------
# SAFE CREDIT FUNCTION
# -------------------------------
def credit_decision(cibil, income, emi, enquiries, dpd30, dpd60, dpd90):

    # Avoid division error
    if income == 0:
        foir = 0
    else:
        foir = emi / income

    # Simple safe scoring
    score = (cibil/10) - (foir*50) - (enquiries*2)

    # Simple probability
    probability = min(max((700 - cibil)/100 + foir + enquiries*0.05, 0), 1)
    probability_percent = round(probability * 100, 2)

    # RULES
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

    # Risk
    if probability_percent < 30:
        risk = "LOW"
    elif probability_percent < 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    return probability_percent, round(score, 2), decision, risk, round(foir*100, 2)


# -------------------------------
# ROUTE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        try:
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
            result = {
                "decision": "ERROR",
                "probability": "-",
                "score": "-",
                "risk": "-",
                "foir": "-",
                "error": str(e)
            }

    return render_template("index.html", result=result)


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)