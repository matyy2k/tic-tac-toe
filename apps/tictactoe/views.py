from flask import Blueprint, flash, redirect, render_template, request, url_for

app_tic = Blueprint("app", __name__)


@app_tic.route("/")
def home():
    return "dsf"
