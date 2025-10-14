#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import os

from fit_common.core.pdf_report_builder import PdfReportBuilder, ReportType
from fit_configurations.controller.tabs.general.legal_proceeding_type import (
    LegalProceedingTypeController,
)
from fit_configurations.utils import get_language

from fit_verify_pec.lang import load_translations


class GenerateReport:

    def pdf_creator(self, report_info):
        self.translations = load_translations()

        signature = self.translations["SIGNATURE_NOT_EXIST"]
        if report_info.get("is_signature"):
            signature = self.translations["SIGNATURE_EXIST"]

        integrity = self.translations["INTEGRITY_FAIL"]
        if report_info.get("is_integrity"):
            integrity = self.translations["INTEGRITY_SUCCESS"]

        provider_name = report_info.get("provider_name")
        is_on_agid_list = self.translations["PROVIDER_IS_NOT_ON_AGID_LIST"].format(
            provider_name
        )
        if report_info.get("is_on_agid_list"):
            is_on_agid_list = self.translations["PROVIDER_IS_ON_AGID_LIST"].format(
                provider_name
            )

        revoked = self.translations["PEC_ADDRESS_IS_NOT_REVOKED"]
        if report_info.get("is_revoked"):
            revoked = self.translations["PEC_ADDRESS_IS_REVOKED"]

        self.__generate(
            report_info.get("to"),
            report_info.get("reply_to"),
            report_info.get("subject"),
            report_info.get("send_date"),
            report_info.get("expiration_date"),
            integrity,
            revoked,
            signature,
            provider_name,
            is_on_agid_list,
            report_info.get("case_info"),
            report_info.get("ntp"),
            report_info.get("eml_file_path"),
        )

    def __generate(
        self,
        to,
        replay_to,
        subject,
        send_date,
        expiration_date,
        integrity,
        revoked,
        signature,
        provider_name,
        is_on_agid_list,
        case_info,
        ntp,
        eml_file_path,
    ):
        case_index = subject.find("case: ")
        case_slice_before = subject[:case_index]
        case_slice_after = subject[case_index:]
        subject = case_slice_before + "\n" + case_slice_after

        folder = os.path.dirname(eml_file_path)
        info_file_path = f"{folder}/pec_info.txt"
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(info_file_path, "w") as file:
            file.write(f"{self.translations['REPORT_LABEL_DETAILS']}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_TO']}\n")
            file.write(f"{to}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_REPLAY_TO']}\n")
            file.write(f"{replay_to}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_SUBJECT']}\n")
            file.write(f"{subject}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_SEND_DATE']}\n")
            file.write(f"{send_date}\n")
            file.write(
                "======================================================================\n"
            )
            file.write("\n")
            file.write(f"{self.translations['REPORT_LABEL_RESULTS']}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_EXPIRATION_DATE']}\n")
            file.write(f"{expiration_date}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_SIGNATURE']}\n")
            file.write(f"{signature}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_INTEGRITY']}\n")
            file.write(f"{integrity}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_REVOKED']}\n")
            file.write(f"{revoked}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_PROVIDER_NAME']}\n")
            file.write(f"{provider_name}\n")
            file.write(
                "======================================================================\n"
            )
            file.write(f"{self.translations['REPORT_LABEL_PROVIDER_CHECK']}\n")
            file.write(f"{is_on_agid_list}\n")
            file.write(
                "======================================================================\n"
            )

        language = get_language()
        translations = (
            load_translations(lang="it")
            if language == "Italian"
            else load_translations()
        )
        case_info[
            "proceeding_type_name"
        ] = LegalProceedingTypeController().get_proceeding_name_by_id(
            case_info.get("proceeding_type", 0)
        )

        report = PdfReportBuilder(
            ReportType.VERIFY,
            translations=translations,
            path=folder,
            filename="report_integrity_pec_verification.pdf",
            case_info=case_info,
        )
        report.ntp = ntp
        report.verify_info_file_path = info_file_path
        report.generate_pdf()
