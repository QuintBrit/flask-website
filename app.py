from flask import Flask, render_template
import main
from git import Repo

app = Flask(__name__, template_folder="templates")

main.build_table(main.bazaar_flipper(), "./templates/flipper_data.html")
#Repo.clone_from("https://github.com/Moulberry/NotEnoughUpdates-REPO.git", "./neu-repo/")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bazaarflipper", methods=["GET", "POST"])
def flipper():
    return render_template("bazaarflipper.html")



if __name__ == "__main__":
    app.run()



