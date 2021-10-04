from flask import Flask, render_template
import BazaarFlipper
from git import Repo

app = Flask(__name__, template_folder="templates")

BazaarFlipper.build_table()
Repo.clone_from("https://github.com/Moulberry/NotEnoughUpdates-REPO.git", "./neu-repo/")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bazaarflipper", methods=["GET", "POST"])
def flipper():
    return render_template("bazaarflipper.html")



if __name__ == "__main__":
    app.run()



