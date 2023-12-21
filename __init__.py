# -----------------------------------------------------------
# Copyright (C) 2023 MapStand Limited
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------
import os
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject, QgsAction
from .form import MapStandEditsFilteringDialog


def classFactory(iface):
    return MapStandEditsFilteringPlugin(iface)


class MapStandEditsFilteringPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dialog = None

    def initGui(self):
        def on_project_changed():
            self.reset()

        self.action = QAction("Edits Filtering", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        QgsProject.instance().readProject.connect(on_project_changed)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):

        if self.dialog is None:
            self.dialog = MapStandEditsFilteringDialog(
                self.iface, self.iface.mainWindow()
            )
        self.dialog.show()

    def reset(self):
        print("reset")
        if self.dialog is not None:
            self.dialog.hide()
            self.dialog = None
