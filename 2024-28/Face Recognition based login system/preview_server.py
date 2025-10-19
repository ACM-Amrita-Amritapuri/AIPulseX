from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def preview():
    return render_template("auth_ui.html")


if __name__ == "__main__":
    app.run(debug=True)
