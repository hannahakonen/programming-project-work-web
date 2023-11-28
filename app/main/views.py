from flask import render_template, redirect, url_for, abort, flash, request, jsonify, current_app
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
import numpy as np
from . import main # turha? ei tuonut mainconfigia
from .config import MainConfig

UPLOAD_FOLDER = 'uploads' # THIS TO ENV

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt'}

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.findall(r'(\S+)\s*,\s*(\S+)', content)
        x_values, y_values = zip(*map(lambda x: (float(x[0]), float(x[1])), matches))
        return list(x_values), list(y_values)

def calculate_y():
    pass

def draw_stem_plot(i, frequencies, intensities): 
    stem_plot = go.Scatter(
        x=[frequencies, frequencies],
        y=[0, intensities],
        mode="lines",
        line=dict(color="dark red"),
        name=f"stemTrace_{i}",  # Use a unique identifier (e.g., index)
        showlegend=False,
        hoverinfo="x+y",
    )  
    return stem_plot

def set_sigma(fwhm):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    return sigma

def draw_simulated_plot(frequencies, intensities, fwhm):  
    fwhm_at_max =  2 * (np.sqrt(np.log(2))) / (np.sqrt(np.pi))
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    x_stop = frequencies[-1] + 10
    x_start = 0 #frequencies[0] - 50
    x = np.linspace(x_start, int(x_stop), 10000)
    sum_y = 0
    number_peaks = len(frequencies)
    scaling_factor = fwhm / fwhm_at_max
    fx = 0
    for i in range(number_peaks):
        fx = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(- (x - frequencies[i])**2 / (2 * sigma**2))
        sum_y += scaling_factor * fx * intensities[i]

    #simulated_plot = go.Scatter(x=frequencies, y=intensities, mode="lines", line=dict(color="black"), hoverinfo="x+y")
    simulated_plot = go.Scatter(x=x, y=sum_y, mode="lines", line=dict(color="black"), name="simulated plot", hoverinfo="x+y")
    return simulated_plot

@main.route("/", methods=['GET', 'POST'])
def index():
    frequencies = MainConfig.FREQUENCIES
    intensities = MainConfig.INTENSITIES
    fwhm = float(1)
      # x=X, ymax=Y, fx=1, ca. 0.94

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
            frequencies, intensities = read_text_file(file_path)
            MainConfig.FREQUENCIES = frequencies
            MainConfig.INTENSITIES = intensities

    fig = go.Figure(layout=go.Layout(
            title=go.layout.Title(text="Raman Spectrum"),
            xaxis=dict(
                title="Frequency (1/cm)",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(frequencies)+0.1) / 10)) * 10],
                dtick=10,
            ),
            yaxis=dict(
                title="Intensity",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(intensities)+0.1) / 10)) * 10],
                dtick=10,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            width=500,
            height=400,
        ),)

    # Create vertical lines for the stems using separate line plots
    for i, (x, y) in enumerate(zip(frequencies, intensities), start=1):
        stem_trace = draw_stem_plot(i, x, y)
        fig.add_trace(stem_trace)

    '''
    for i, (frequencies, intensities) in enumerate(zip(frequencies, intensities), start=1):
        stem_trace = go.Scatter(
            x=[frequencies, frequencies],
            y=[0, intensities],
            mode="lines",
            line=dict(color="red"),
            name=f"stemTrace_{i}",  # Use a unique identifier (e.g., index)
            showlegend=False,
            hoverinfo="x+y",
        )
        fig.add_trace(stem_trace)
    '''

    # Create the simulated trace using a method
    simulated_plot = draw_simulated_plot(frequencies=frequencies, intensities=intensities, fwhm=fwhm) #initial_fwhm, fwhm_at_max)
    fig.add_trace(simulated_plot)

    '''
    fig = go.Figure(
        data=[
            go.Scatter(x=frequencies, y=intensities, mode="lines", line=dict(color="black"), hoverinfo="x+y") 
        ],
        layout=go.Layout(
            title=go.layout.Title(text="Raman Spectrum"),
            xaxis=dict(
                title="Frequency (1/cm)",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(frequencies)+0.1) / 10)) * 10],
                dtick=10,
            ),
            yaxis=dict(
                title="Intensity",
                showline=True,
                # linewidth=1,
                linecolor="black",
                mirror=True,
                range=[0, (math.ceil((max(intensities)+0.1) / 10)) * 10],
                dtick=10,
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            width=500,
            height=400,
        ),
    )
    '''

    # This works but not possible to have specifid names for each stem/peak
    # for x, y in zip(x_stem, y_stem):
    # fig.add_trace(go.Scatter(x=[x, x], y=[0, y], mode='lines', line=dict(color='red'), name='stemScatter', showlegend=False))

    # Convert the plot to graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("index.html", graphJSON=graphJSON, frequencies=frequencies, intensities=intensities, draw_simulated_plot=draw_simulated_plot, initialZ=fwhm)

@main.route('/update_plot', methods=['POST'])
def update_plot():
    frequencies = MainConfig.FREQUENCIES
    intensities = MainConfig.INTENSITIES
    data = request.get_json()
    fwhm = float(data['newValue'])

    # Perform calculations using new_value
    # Example: Calculate newYValues using draw_simulated_plot or other method
    new_simulated_plot = draw_simulated_plot(frequencies=frequencies, intensities=intensities, fwhm=fwhm) #initial_fwhm, fwhm_at_max)
  
    # Respond with the updated plot data
    response = {'newYValues': new_simulated_plot.y.tolist()}  # Convert y values to a list
    #response = {'newYValues': plot_data}
    return jsonify(response)

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
