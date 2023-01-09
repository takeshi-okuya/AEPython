# Render and Email

import AEPython as ae

from support import ChangeEmailSettings, email_methods

scriptName = "Render and Email"


def RenderAndEmail():
    safeToRunScript:bool = ae.app.project is not None
    if ae.app.project is None:
        ae.alert ("A project must be open to use this script.", scriptName)

    if safeToRunScript:
        # Check the render queue and make certain at least one item is queued.
        safeToRunScript = False
        for i in range(1, ae.app.project.renderQueue.numItems + 1):
            if ae.app.project.renderQueue.item(i).status == ae.RQItemStatus.QUEUED:
                safeToRunScript = True
                break
        if safeToRunScript == False:
            ae.alert("You do not have any items set to render.", scriptName)

    if safeToRunScript:
        # Check if we are allowed to access the network.
        securitySetting = ae.app.preferences.getPrefAsLong("Main Pref Section", "Pref_SCRIPTING_FILE_NETWORK_SECURITY")
        if securitySetting != 1:
            ae.alert ("This script requires the scripting security preference to be set.\n" +
                "Go to the \"General\" panel of your application preferences,\n" +
                "and make sure that \"Allow Scripts to Write Files and Access Network\" is checked.", scriptName)
            safeToRunScript = False
    
    if safeToRunScript:
        # The script email_setup.jsx will prompt the user and establish the settings.
        # We'll only run it now if we don't have the settings already. 
        # If you want to change the settings, you can run email_setup.jsx as a 
        # separate script at any time.
        settings = ae.app.settings
        if settings.haveSetting("Email Settings", "Mail Server") == False or\
           settings.haveSetting("Email Settings", "Reply-to Address") == False or\
           settings.haveSetting("Email Settings", "Render Report Recipient") == False:
            # We don't have the settings yet, so run Change Email Settings.jsx to prompt for them.
            ChangeEmailSettings.ChangeEmailSettings()

        myQueue = ae.app.project.renderQueue # Creates a shortcut for the Render Queue.
        
        # Start rendering.
        myQueue.render()

        # Now rendering is complete.
        # Create a string for the mail message that contains:
        # -- Start time (date);
        # -- Render time of each item in the queue;
        # -- Total render time.
        projectName = "Unsaved Project"
        if ae.app.project.file is not None:
            projectName = ae.app.project.file.name
        # Can't have bare LF in email, Always put \r before \n or some servers will die.
        myMessage = "Rendering of " + projectName + " is complete.\r\n\r\n"
        
        # Email the message.
        # We'll use three settings to determine how to mail.
        # The section will be named "Email Settings".
        # The 3 settings will be named:
        # -- "Mail Server" - the mail server to use when sending mail.
        # -- "Reply-to Address" - the address from which the mail will be sent.
        # -- "Render Report Recipient" - the address to which mail will be sent.
        if settings.haveSetting("Email Settings", "Mail Server") == False or\
           settings.haveSetting("Email Settings", "Reply-to Address") == False or\
           settings.haveSetting("Email Settings", "Render Report Recipient") == False:
            ae.alert("Can't send email; I don't have all the settings I need. Aborting.", scriptName)
        else:
            try:
                # Send the email.
                serverSetting = settings.getSetting("Email Settings", "Mail Server")
                fromSetting = settings.getSetting("Email Settings", "Reply-to Address")
                toSetting = settings.getSetting("Email Settings", "Render Report Recipient")
                authUser = None
                authPass = None

                if ae.app.settings.haveSetting("Email Settings", "Auth User"):
                    authUser = ae.app.settings.getSetting("Email Settings", "Auth User")

                if ae.app.settings.haveSetting("Email Settings", "Auth Pass"):
                    authPass = ae.app.settings.getSetting("Email Settings", "Auth Pass")
                
                # Ack, can't delete settings...
                if authUser == "":
                    authUser = None
                    authPass = None

                errs = email_methods.send_tls(serverSetting, 587, fromSetting, toSetting, "AE Render Completed", myMessage, authUser, authPass)
                if len(errs) > 0:
                    ae.alert("Sending mail failed.", scriptName)
                    print(errs)
            except:
                import traceback
                ae.alert("Unable to send email.\n" + traceback.format_exc(), scriptName)
                traceback.print_exc()


RenderAndEmail()
