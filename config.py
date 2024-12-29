####################################################
# Web Ticket
#
# 
# Project : Flask, Python
# Author  : Thanapoom Sukarin, Tonson Ubonsri and KK Team
# Modifier: 
# Version : 
# Date    : Dec 01, 2024
#
####################################################

# config.py: เก็บการตั้งค่าทั้งหมดของแอป
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mykey')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
