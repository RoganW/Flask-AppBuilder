import calendar
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from flask_appbuilder.models.sqla.filters import FilterStartsWith
from flask_appbuilder import SimpleFormView
from wtforms.fields import TextField
from flask_appbuilder.widgets import FormHorizontalWidget, FormInlineWidget, FormVerticalWidget
from flask_babel import lazy_gettext as _


from app import db, appbuilder
from .models import ContactGroup, Gender, Contact, ContactGroupView


def fill_gender():
    try:
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()
    except:
        db.session.rollback()


class ContactGroupViewModelView(ModelView):
    base_permissions = ['can_list','can_show']
    datamodel = SQLAInterface(ContactGroupView)
    list_columns = ['group_name', 'group_count']


class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group.name']

    base_order = ('name', 'asc')


class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]


class ContactChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)
    chart_title = 'Grouped contacts'
    label_columns = ContactModelView.label_columns
    chart_type = 'PieChart'

    definitions = [
        {
            'group' : 'contact_group',
            'series' : [(aggregate_count,'contact_group')]
        },
        {
            'group' : 'gender',
            'series' : [(aggregate_count,'contact_group')]
        }
    ]


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


def pretty_year(value):
    return str(value.year)


class ContactTimeChartView(GroupByChartView):
    datamodel = SQLAInterface(Contact)

    chart_title = 'Grouped Birth contacts'
    chart_type = 'AreaChart'
    label_columns = ContactModelView.label_columns
    definitions = [
        {
            'group' : 'month_year',
            'formatter': pretty_month_year,
            'series': [(aggregate_count, 'group')]
        },
        {
            'group': 'year',
            'formatter': pretty_year,
            'series': [(aggregate_count, 'group')]
        }
    ]


db.create_all()
fill_gender()
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-folder-open-o", category="Contacts", category_icon='fa-envelope')
appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(ContactGroupViewModelView, "Contacts By Group View", icon="fa-dashboard", category="Contacts")
appbuilder.add_separator("Contacts")
appbuilder.add_view(ContactChartView, "Contacts Chart", icon="fa-dashboard", category="Contacts")
appbuilder.add_view(ContactTimeChartView, "Contacts Birth Chart", icon="fa-dashboard", category="Contacts")
