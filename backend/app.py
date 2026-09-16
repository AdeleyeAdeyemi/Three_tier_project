from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="src/presentation/pages"
)


@app.route("/")
def home():
    return render_template(
        "display_features.html",
        timestamp="2026-09-16 12:00",
        title="Platform is running",
        messages=["Application started successfully"],
        errors=[]
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
