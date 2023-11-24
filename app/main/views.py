from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required
import pandas as pd
import json
import plotly
import plotly.graph_objects as go
import plotly.express as px
import math
import re
import os

UPLOAD_FOLDER = 'uploads' # THIS TO ENV

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt'}

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.findall(r'(\S+)\s*,\s*(\S+)', content)
        x_values, y_values = zip(*map(lambda x: (float(x[0]), float(x[1])), matches))
        return list(x_values), list(y_values)


@main.route("/", methods=['GET', 'POST'])
def index():
    #x = [1, 2.2, 3.7, 14, 15, 30, 35, 60, 62.4, 64]
    #y = [2, 14, 8, 5, 9, 31.5, 20, 6, 10, 5]

    x = [0]
    y = [0]

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file
        if file.filename == '':
            return render_template('index.html', error='No selected file')

        # If the file is allowed and has a valid extension
        if file and allowed_file(file.filename):
            # Save the file to the uploads folder
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)  #app.config['UPLOAD_FOLDER']
            file.save(file_path)

            # Read the content of the uploaded file
            x, y = read_text_file(file_path)

    fig = go.Figure(
        data=[
            go.Line(x=x, y=y, mode="lines", line=dict(color="black"), hoverinfo="x+y")
        ],
        layout=go.Layout(
            title=go.layout.Title(text="Unsorted Input"),
            xaxis=dict(
                title="Frequency (1/cm)",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(x)+0.1) / 10)) * 10],
                dtick=10,
            ),
            yaxis=dict(
                title="Intensity",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(y)+0.1) / 10)) * 10],
                dtick=10,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            width=600,
            height=400,
        ),
    )

    # This works but not possible to have specifid names for each stem/peak
    # for x, y in zip(x_stem, y_stem):
    # fig.add_trace(go.Scatter(x=[x, x], y=[0, y], mode='lines', line=dict(color='red'), name='stemScatter', showlegend=False))

    # Create vertical lines for the stems using separate line plots
    for i, (x, y) in enumerate(zip(x, y), start=1):
        stem_trace = go.Scatter(
            x=[x, x],
            y=[0, y],
            mode="lines",
            line=dict(color="red"),
            name=f"stemTrace_{i}",  # Use a unique identifier (e.g., index)
            showlegend=False,
            hoverinfo="x+y",
        )

        fig.add_trace(stem_trace)
    
    # Convert the plot to graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("index.html", graphJSON=graphJSON)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash("Your profile has been updated.")
        return redirect(url_for(".user", username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for(".user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form, user=user)
