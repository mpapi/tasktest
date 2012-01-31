from tasktest import task, started, finished

@finished(milestone=1, assignee='matt')
def implement_file_uploads():
    '''
    A logged-in user should be able to upload a file of any type using the file
    upload menu in the dropdown.
    '''
    assert False

@started(milestone=1, assignee='matt')
def right_column_cta():
    '''
    Add a giant neon orange call-to-action button in the right column above all
    the ads.
    '''
    assert True

@task(milestone=2, bug=True)
def firefox_csv_export_link():
    '''
    The "CSV export" link causes JavaScript errors in Firefox. It should open
    the CSV export options dialog.
    '''
    pass

@task(milestone=2)
def email_notifications():
    '''
    Send email notifications to all users in the system whenever a user edits
    anything on the site.
    '''
    pass
