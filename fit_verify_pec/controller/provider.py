#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: LGPL-3.0-or-later
# -----
######

import requests
from bs4 import BeautifulSoup


class Provider:
    def __init__(self, temp_x509):
        self.x509_file_path = temp_x509
        self.url = "https://www.agid.gov.it/it/piattaforme/posta-elettronica-certificata/elenco-gestori-pec"

    def get_provider_name(self):
        provider = None
        with open(self.x509_file_path, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                word = "Subject: "
                if row.find(word) != -1:
                    if " O = " in row:
                        provider = row.split(" O = ")[1]
                        provider = provider.split(", ")[0]
                    elif " O=" in row:
                        provider = row.split(" O=")[1]
                        provider = provider.split(", ")[0]
        return provider

    def check_if_provider_is_on_agid_list(self, provider_name):
        page_num = 0
        found = False

        while True:
            response = requests.get(f"{self.url}?page={page_num}")
            soup = BeautifulSoup(response.text, "html.parser")

            if provider_name in soup.get_text():
                found = True

            next_button = soup.find("a", {"rel": "next"})
            if next_button is None:
                break
            else:
                page_num += 1

        return found
