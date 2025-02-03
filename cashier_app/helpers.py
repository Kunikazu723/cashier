from flask import render_template
def apology(txt) :
    return render_template('apology.html', text=txt)

def to_reais(double) :
    double = float(double)
    return f"R${double:.2f}"