#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import subprocess
from datetime import datetime
from email import policy
from email.parser import BytesParser

from fit_common.core import get_platform, is_cmd, resolve_path


class ExpirationDate:
    def verify(self, eml_file_path, pem_file_path, x509_file_path, textdata_file_path):
        result = {}
        openssl = "openssl"
        is_installed_openssl = is_cmd(openssl)

        if is_installed_openssl is False:
            openssl = resolve_path("ext_lib/openssl/{}/openssl".format(get_platform()))
        # extract pem certificate from eml
        extract_pem = subprocess.run(
            [
                openssl,
                "smime",
                "-verify",
                "-in",
                eml_file_path,
                "-noverify",
                "-signer",
                pem_file_path,
                "-out",
                textdata_file_path,
            ],
            capture_output=True,
            text=True,
        )

        # Convert pem to x509 without invoking a shell.
        if extract_pem.returncode == 0:
            convert_x509 = subprocess.run(
                [openssl, "x509", "-in", pem_file_path, "-text"],
                capture_output=True,
                text=True,
            )
            if convert_x509.returncode != 0:
                raise Exception(convert_x509.stderr)
            with open(x509_file_path, "w", encoding="utf-8") as x509_file:
                x509_file.write(convert_x509.stdout)
            result = self.__check_date(eml_file_path, x509_file_path)
        else:
            raise Exception(extract_pem.stderr)

        return result

    def __check_date(self, eml_file_path, x509_file_path):
        date_s = None

        with open(x509_file_path, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                word = "Not After"
                if row.find(word) != -1:
                    date_s = row

        with open(eml_file_path, "rb") as fp:
            msg = BytesParser(policy=policy.default).parse(fp)

        # expiration date
        if date_s is not None:
            date_s = date_s.split(" : ")[1]
            date_s = date_s.split(" G")[0]
            date_s = datetime.strptime(date_s, "%b %d %I:%S:%M %Y")

        return {
            "expiration_date": date_s,
            "reply_to": msg["Reply-To"],
            "to": msg["To"],
            "subject": msg["Subject"],
            "send_date": msg["Date"],
        }
