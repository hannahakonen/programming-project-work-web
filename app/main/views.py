from flask import render_template, redirect, url_for, abort, flash
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


@main.route('/')
def index():   
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    fig = go.Figure(data=[go.Line(x=x, y=y)],layout=go.Layout(title=go.layout.Title(text="Unsorted Input")))   

    # This works but not possible to have specifid names for each stem/peak
    #for x, y in zip(x_stem, y_stem):
        #fig.add_trace(go.Scatter(x=[x, x], y=[0, y], mode='lines', line=dict(color='red'), name='stemScatter', showlegend=False))

    # Create vertical lines for the stems using separate line plots
    for i, (x, y) in enumerate(zip(x, y), start=1):
        stem_trace = go.Scatter(
            x=[x, x],
            y=[0, y],
            mode='lines',
            line=dict(color='red'),
            name=f'stemTrace_{i}',  # Use a unique identifier (e.g., index)
            showlegend=False
        )

        fig.add_trace(stem_trace)

    # Convert the plot to graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
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
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
