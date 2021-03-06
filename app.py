# Copyright (c) 2018 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys

from sgtk.platform import Application

class SetupProject(Application):
    """
    An app that will allow an admin user to setup a project to use an advanced
    configuration. When launched, a setup wizard will walk the user through
    setting the project up, including selection of a configuration to use and
    where everything will be installed on disk.
    """
    def init_app(self):
        """
        Called as the application is being initialized.
        """
        # Setup our callback and register the command with the engine.
        menu_callback = lambda : self._run_setup()
        self.engine.register_command("Advanced Project Setup...", menu_callback)

    def _run_setup(self):
        """
        Launches the project setup wizard!
        """
        # We're not using engine.show_dialog for this, because the SetupProjectWizard
        # is itself a QWizard, which subclasses QDialog. Wrapping the dialog in our
        # own dialog results in some very odd behavior from things like the wizard's
        # cancel button. Rather than try to figure out how to pass reject/accept/etc
        # signals up to a wrapper dialog, we'll just use the wizard directly. The only
        # downsides to this are that we don't get our typical Toolkit header at the
        # top of the dialog, which is not a big deal in this case, and we'd likely end
        # up with styling issues if this were run in an engine with engine-level qss
        # being applied (ie: tk-houdini, tk-rv, and maybe 1-2 others). Since this is
        # an app used exclusively by tk-shotgun, though, we're just fine. The "dark
        # look and feel" applied on engine init there all operates on the parent
        # QApplication, which the wizard will inherit automatically.
        setup_project = self.frameworks["tk-framework-adminui"].import_module("setup_project")
        self._setup_wizard = setup_project.SetupProjectWizard(
            project=self.engine.context.project,
        )

        from sgtk.platform.qt import QtCore

        # We want this to be forced on top, but we don't need to do that on OSX. Oddly,
        # doing so on OSX causes stability problems on launch, but it's a non-issue,
        # because the dialog launches on top by itself on that OS. We have problems on
        # CentOS 6 and Windows 10 where it pops up behind everything, so this is the
        # heavy-handed approach to resolving that.
        if sys.platform != "darwin":
            self._setup_wizard.setWindowFlags(self._setup_wizard.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self._setup_wizard.exec_()

        # Once we're done, calling shutdown will ensure we're not leaving any threads
        # running. Hiding the dialog is an odd requirement for the external_config API. The
        # wizard doesn't appear to be garbage collected once it's closed the way most
        # other dialogs are, so there's a provision in external_config to also check
        # whether any widgets are visible before closing down its QApplication when
        # finishing up with an external process.
        self._setup_wizard.shutdown()
        self._setup_wizard.hide()
        
