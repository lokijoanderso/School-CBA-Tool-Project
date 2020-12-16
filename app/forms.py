from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NoneOf
from app import fields
import temp

defval = ("-1", "Select a Choice" )
edufield = [defval] + fields.educ_levels
explevel = [defval] + fields.exp_levels
states = [defval] + fields.build_state_opts()
careers, pathways, links = fields.build_career_opts()
careers = [defval] + careers
pathways = [defval] + pathways

class CareerForm(FlaskForm):

    career = SelectField('Career Field',
                         validators=[NoneOf(["-1"],
                         message="select a field to search")],
                         choices=careers, default="-1")

    pathway = SelectField('Career Area')

    state = SelectField('State to Work In',
                        validators=[NoneOf(["-1"],
                        message="select your state")],
                        choices=states, default=["-1"])

    education = SelectField("Highest Current Level of Education",
                            validators=[NoneOf(["-1"],
                            message="select your education level")],
                            choices=edufield, default=["-1"])

    experience = SelectField("Years of Work Experience in Field",
                            validators=[NoneOf(["-1"],
                            message="select your experience level")],
                            choices=explevel, default=["-1"])

    submit = SubmitField("Search")
    clear = SubmitField("Clear")
    choose = SubmitField("Select Field")

    return_data = None

    test_bls = SubmitField("test BLS data")
    test_onet = SubmitField("test O*NET data")
    test_educ = SubmitField("test educ data")


    def paths_for_career(self, data):
        '''
        generate a filtered list of pathways for each
        career area to keep those drop downs tidy.
        '''

        valid_codes = links.get(data, ["-1"])
        path_choices = []

        for code, choice in pathways:
            if code in valid_codes:
                path_choices.append((code, choice))

        return path_choices

