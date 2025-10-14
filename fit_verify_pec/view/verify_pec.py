# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import os

from fit_cases.view.case_form_dialog import CaseFormDialog
from fit_common.core import get_version
from fit_common.core.utils import get_ntp_date_and_time
from fit_common.gui.utils import (
    Status,
    VerificationTypes,
    add_label_in_verification_status_list,
    get_verification_label_text,
    show_finish_verification_dialog,
)
from fit_configurations.controller.tabs.general.general import (
    GeneralController as GeneralConfigurationController,
)
from fit_configurations.controller.tabs.network.network_check import (
    NetworkCheckController,
)
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QFileDialog

from fit_verify_pec.controller.verify_pec import (
    verifyPec as verifyPecController,
)
from fit_verify_pec.lang import load_translations
from fit_verify_pec.view.verify_pec_ui import (
    Ui_fit_verify_pec,
)


class VerifyPec(QtWidgets.QMainWindow):

    def __init__(self, wizard=None):
        super(VerifyPec, self).__init__(wizard)
        self.acquisition_directory = None
        self.wizard = wizard
        self.verify_pec_controller = verifyPecController()

        self.translations = load_translations()

        self.__init_ui()

    def __init_ui(self):
        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui = Ui_fit_verify_pec()
        self.ui.setupUi(self)

        # CUSTOM TOP BAR
        self.ui.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.ui.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.ui.close_button.clicked.connect(self.close)

        # SET VERSION
        self.ui.version.setText(f"v{get_version()}")

        # EML FOLDER BUTTON
        self.ui.eml_folder_button.clicked.connect(self.__select_eml_file)

        # VERIFICATION BUTTON
        self.ui.verification_button.clicked.connect(self.__verify)
        self.ui.verification_button.setEnabled(False)

        # DISABLE VERIFY BUTTON IF FIELD IS EMPTY
        self.ui.eml_folder_input.textChanged.connect(self.__enable_verify_button)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __enable_verify_button(self):
        self.ui.verification_button.setEnabled(bool(self.ui.eml_folder_input.text()))

    def __select_eml_file(self):
        file, check = QFileDialog.getOpenFileName(
            None,
            self.translations["OPEN_EML_FILE"],
            os.path.expanduser(
                GeneralConfigurationController().configuration.get("cases_folder_path")
            ),
            self.translations["EML_FILES"],
        )
        if check:
            self.ui.eml_folder_input.setText(file)

    def __verify(self):

        self.ui.verification_status_list.clear()
        signature = {}
        is_revoked = False
        is_integrity = False
        provider_name = ""
        is_on_agid_list = False

        verification_status, email_info = self.__check_expirationdate()

        if verification_status == Status.SUCCESS:
            if len(email_info) > 0:
                signature = self.__check_signature_exist()
                is_revoked = self.__check_revoked()
                is_integrity = True
                provider_name, is_on_agid_list = self.__check_autority()

            else:
                label = "INFO: {}".format(
                    self.translations["NO_MAIL_INFO_FOUD_AFTER_CHECK_EXPIRATIONDATE"]
                )
                add_label_in_verification_status_list(
                    self.ui.verification_status_list, label
                )
                email_info = self.__get_mail_info_from_eml()
                signature = self.__check_signature_exist()

            eml_file_path = self.ui.eml_folder_input.text()
            path = os.path.dirname(str(eml_file_path))
            ntp = get_ntp_date_and_time(
                NetworkCheckController().configuration["ntp_server"]
            )
            case_info = CaseFormDialog().get_case_info(path)

            report_info = {
                "case_info": case_info,
                "ntp": ntp,
                "eml_file_path": eml_file_path,
                "is_integrity": is_integrity,
                "is_revoked": is_revoked,
                "provider_name": provider_name,
                "is_on_agid_list": is_on_agid_list,
            }
            report_info.update(email_info)
            report_info.update(signature)

            if self.__generate_report(report_info) == Status.SUCCESS:
                show_finish_verification_dialog(path, VerificationTypes.PEC)
        else:
            label = "INFO: {}".format(self.translations["CHECK_EXPIRATIONDATE_FAIL"])
            add_label_in_verification_status_list(self.verification_status_list, label)

    def __check_expirationdate(self):

        email_info = dict()
        verification_status = Status.SUCCESS
        verification_name = self.translations["CHECK_EXPIRATIONDATE"]
        verification_message = ""

        try:
            email_info = self.verify_pec_controller.check_expirationdate(
                self.ui.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return verification_status, email_info

    def __check_signature_exist(self):

        signature = {}
        verification_status = Status.SUCCESS
        verification_name = self.translations["CHECK_SIGNATURE"]
        verification_message = ""
        try:
            signature = self.verify_pec_controller.check_signature_exist(
                self.ui.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return signature

    def __check_revoked(self):

        is_revoked = False
        verification_status = Status.SUCCESS
        verification_name = self.translations["CHECK_REVOKED"]
        verification_message = ""
        try:
            is_revoked = self.verify_pec_controller.check_revoked()
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return is_revoked

    def __check_autority(self):

        provider_name = ""
        is_on_agid_list = False

        verification_status = Status.SUCCESS
        verification_name = self.translations["CHECK_AUTORITY"]
        verification_message = ""
        try:
            provider_name, is_on_agid_list = self.verify_pec_controller.check_autority()
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return provider_name, is_on_agid_list

    def __get_mail_info_from_eml(self):
        email_info = {}
        verification_status = Status.SUCCESS
        verification_name = self.translations["GET_MAIL_INFO_FROM_EML"]
        verification_message = ""
        try:
            email_info = self.verify_pec_controller.get_mail_info_from_eml(
                self.ui.eml_folder_input.text()
            )
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return email_info

    def __generate_report(self, report_info):

        verification_status = Status.SUCCESS
        verification_name = self.translations["GENARATE_REPORT"]
        verification_message = ""
        try:
            self.verify_pec_controller.ganerate_report(report_info)
        except Exception as e:
            verification_status = Status.FAILURE
            verification_message = str(e)

        label = get_verification_label_text(
            verification_name, verification_status, verification_message
        )

        add_label_in_verification_status_list(self.ui.verification_status_list, label)

        return verification_status

    def __back_to_wizard(self):
        self.deleteLater()
        self.wizard.reload_case_info()
        self.wizard.show()

    def closeEvent(self, event):
        if self.wizard is not None:
            event.ignore()
            self.__back_to_wizard()
