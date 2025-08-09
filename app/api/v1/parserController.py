from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
from app.services.bankRouter import route_to_bank_parser


router = APIRouter()


