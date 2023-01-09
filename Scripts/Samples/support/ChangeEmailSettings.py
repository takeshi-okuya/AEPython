# Change Email Settings.jsx
#
# This script sets email settings. It can be run all by itself, but it is also
# called within Render and Email.jsx if the settings aren't yet set.

import AEPython as ae


def ChangeEmailSettings():
    def GetStringDefaultNull(key):
        if ae.app.settings.haveSetting("Email Settings", key):
            return ae.app.settings.getSetting("Email Settings", key)
        else:
            return ""

    serverValue = ae.prompt("Enter smtp server address:", GetStringDefaultNull("Mail Server"))
    if serverValue is None:
        return

    fromValue = ae.prompt("Enter reply-to email address:", GetStringDefaultNull("Reply-to Address"))
    if fromValue is None:
        return

    requiresAuth = ae.confirm("Does your smtp server require you to log in?")
    authUser = GetStringDefaultNull("Auth User")
    authPass = GetStringDefaultNull("Auth Pass")

    if requiresAuth == True:
        authUser = ae.prompt("Please enter the login id for the server:", authUser)
        if authUser is None:
            return

        if authUser is not None:
            authPass = ae.prompt("Please enter the password for the server:", "")
            if authPass is None:
                return

        if authUser is not None:
            ae.app.settings.saveSetting("Email Settings", "Auth User", authUser)

        if authPass is not None:
            # ae.app.settings.saveSetting("Email Settings", "Auth Pass", encodeBase64(authPass))
            ae.app.settings.saveSetting("Email Settings", "Auth Pass", authPass)
    else:
         ae.app.settings.saveSetting("Email Settings", "Auth User", "")
         ae.app.settings.saveSetting("Email Settings", "Auth Pass", "")

    toValue = ae.prompt("Enter recipient's email address", GetStringDefaultNull("Render Report Recipient"))

    if toValue is None:
        return

    if serverValue is not None and serverValue != "":
         ae.app.settings.saveSetting("Email Settings", "Mail Server", serverValue)

    if fromValue is not None and fromValue != "":
         ae.app.settings.saveSetting("Email Settings", "Reply-to Address", fromValue)

    if toValue is not None and toValue != "":
         ae.app.settings.saveSetting("Email Settings", "Render Report Recipient", toValue)
