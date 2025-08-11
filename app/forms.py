from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, DecimalField, PasswordField,FieldList,FormField, HiddenField,FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6)])
class RSQRForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    justification = TextAreaField('Justification', validators=[DataRequired()])
    deliverables = TextAreaField('Deliverables', validators=[DataRequired()])
    pdf_file = FileField('Upload PDF', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    save = SubmitField('Save')
    next = SubmitField('Next')

class ManagementCouncilForm(FlaskForm):
    council_date = DateField('Meeting Date', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    chairperson = StringField('Chairperson', validators=[Optional()])
    title = StringField('Project Title', validators=[Optional()])
    pdc = StringField('PDC', validators=[Optional()])
    cost = DecimalField('Project Cost (INR)', validators=[Optional()])
    council_pdf = FileField('Upload PDF', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    save = SubmitField('Save')
    next = SubmitField('Next')

class OfferEvaluationForm(FlaskForm):
    offer_eval_date = DateField('Offer Evaluation Committee Date', validators=[DataRequired()])
    eval_chairperson = StringField('Chairperson Name', validators=[DataRequired()])
    eval_member = StringField('Member Name', validators=[DataRequired()])
    eval_user = StringField('User Name', validators=[DataRequired()])
    evaluation_pdf = FileField('Upload PDF', validators=[FileAllowed(['pdf'], 'PDF only!')])
    meeting_location = StringField('Meeting Location', validators=[DataRequired()])
    save = SubmitField('Save')
    next = SubmitField('Next')
    

class SummaryOfferForm(FlaskForm):
    summary_pdf = FileField('Upload PDF', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    save = SubmitField('Save')
    next = SubmitField('Next')
    
class NDASOCForm(FlaskForm):
    nda_pdf = FileField('Upload NDA PDF', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    soc_pdf = FileField('Upload SOC PDF', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    save = SubmitField('Save')
    next = SubmitField('Next')

class DynamicCostEntryForm(FlaskForm):
    category = StringField('Category')
    amount = DecimalField('Amount', validators=[Optional(), NumberRange(min=0)], places=2)

class UONumberForm(FlaskForm):

    uo_number = StringField('UO Number')
    # Fixed cost fields
    personal = DecimalField('Personal', validators=[Optional(), NumberRange(min=0)], places=2)
    equipment = DecimalField('Equipment', validators=[Optional(), NumberRange(min=0)], places=2)
    travel = DecimalField('Travel', validators=[Optional(), NumberRange(min=0)], places=2)
    contingencies = DecimalField('Contingencies', validators=[Optional(), NumberRange(min=0)], places=2)
    visiting_faculty = DecimalField('Visiting Faculty', validators=[Optional(), NumberRange(min=0)], places=2)
    technical_support = DecimalField('Technical Support', validators=[Optional(), NumberRange(min=0)], places=2)
    ipr_fees = DecimalField('IPR Fees', validators=[Optional(), NumberRange(min=0)], places=2)
    overheads = DecimalField('Overheads', validators=[Optional(), NumberRange(min=0)], places=2)
    total_amount = DecimalField('Total Amount', validators=[Optional(), NumberRange(min=0)], places=2)
    gst = DecimalField('GST', validators=[Optional(), NumberRange(min=0)], places=2)
    # Dynamic entries
    dynamic_entries = FieldList(FormField(DynamicCostEntryForm), min_entries=0)


    # Buttons
    save = SubmitField('Save')
    next = SubmitField('Next')

  

class UniqueSanctionForm(FlaskForm):
    sanction_code = StringField('USC Code', validators=[DataRequired()])
    save = SubmitField('Save')
    next = SubmitField('Next')

#contract
class ContractForm(FlaskForm):
    contract_number = StringField('Contract Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    contract_pdf = FileField('Upload Contract (PDF)', validators=[Optional(), FileAllowed(['pdf'])])

    save = SubmitField('Save')
    next = SubmitField('Next')
    

    
#sanctionletterform
class SanctionLetterForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    project_cost = FloatField('Project Cost', validators=[DataRequired()])
    project_duration = IntegerField('Project Duration (months)', validators=[DataRequired()])
    cars_project_no = StringField('CARS Project Number', validators=[DataRequired()])
    availability_of_funds = StringField('Availability of Funds', validators=[DataRequired()])
    uo_code = StringField('UO Code', validators=[Optional()])
    usc_code = StringField('USC Code', validators=[Optional()])
    sanction_pdf = FileField('Upload Sanction Letter PDF', validators=[Optional(), FileAllowed(['pdf'])])
    contract_number = StringField('Contract Number', validators=[Optional()])
    save = SubmitField('Save')
    next = SubmitField('Next')


#amendment form

class AmendmentLetterForm(FlaskForm):
    amendment_no = StringField('Amendment No', validators=[DataRequired()])
    amendment_date = DateField('Amendment Date', validators=[DataRequired()])
    pi = StringField('Principal Investigator', validators=[DataRequired()])
    co_pi = StringField('Co-Principal Investigator', validators=[Optional()])
    institute = StringField('Institute', validators=[DataRequired()])
    project_duration = IntegerField('Project Duration (months)', validators=[DataRequired()])

    amendment_pdf = FileField('Upload Amendment PDF', validators=[Optional()])

    save = SubmitField('Save')
    next = SubmitField('Next')
