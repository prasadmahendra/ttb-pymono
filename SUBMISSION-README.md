# AI-Powered Alcohol Label Verification App  
  
> A full-stack web application that simulates the TTB (Alcohol and Tobacco Tax and Trade Bureau) label approval process using AI-powered OCR to verify alcohol beverage labels against submitted application data.  
  
## 🔗 Links  
  
| Resource | URL |  
|----------|-----|  
| **Live Demo** | https://ttb-webapp.vercel.app/ |  
| **Repository (Webapp)** | https://github.com/prasadmahendra/ttb-webapp |  
| **Repository (Backend)** | https://github.com/prasadmahendra/ttb-pymono |  
  
---  
  
## 📋 Table of Contents  
  
- [Overview](#overview)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Running the app locally](#running-the-app-locally)  
- [Usage](#usage)  
- [Assumptions & Design Decisions](#assumptions--design-decisions)  
- [Known Limitations, Trade-offs](#known-limitations-trade-offs)  
- [Testing](#testing)  
  
---  
  
## Overview  
  
This application allows users to:  
1. Submit product information via a web form (brand name, product type, ABV, net contents)  
2. Upload an alcohol label image  
3. Receive AI-powered verification results comparing the label against the form data  
  
The app uses a multi-modal language model to extract text from label images and performs intelligent matching to determine if the label content matches the submitted application data.  
  
---  
  
## Features  
  
### Core Features  
- [x] **Form Input**: Simplified TTB application form with fields for:  
  - Brand Name  
  - Product Class/Type  
  - Alcohol Content (ABV)  
  - Net Contents  
  - Warnings (Optional, added to the requirements as a Bonus to show flexibility/extensibility) 
- [x] **Image Upload**: Support for JPEG, PNG label images  
- [x] **AI/OCR Processing**: Text extraction from label images using OpenAI (default) or pytesseract
- [x] **Verification and Analysis**: Comparison logic between extracted text and form data using OpenAI or pytesseract pattern matching
- [x] **Results Display**: Clear success/failure indication with detailed field-by-field breakdown  
  
### Bonus Features (X indicates implemented)  
- [x] Government Warning text verification (Left as **optional** in the input form, for purposes of this excercise) 
- [ ] Multiple product type support (Beer, Wine, Spirits)  
- [ ] Image highlighting of detected text regions  
- [x] Polish and UX Improvements:
- [x] Fuzzy matching for OCR error tolerance  
- [x] Database (Postgres) for persistence 
- [x] Unit tests 
  
---  

## Tools, Coding assistants used

**Figma Make**: To Establish the front-end dashboard layout and the design system
**IDE + Claude-Code**:  For example, Claude did most of the heavy lifting on writing unit tests
 
## Tech Stack  
  
| Layer | Technology |  
|-------|------------|  
| **Frontend** | React, Vite, Tail-wind |  
| **Backend** | Python/Flask, Uvicorn, Postgres |  
| **OCR/AI** | OpenAI (default) or pytesseract - configurable via `analysis_mode` |  
| **Deployment** | Vercel |  
| **Other Libraries** | Docker environment for local testing |  
  
---  
  
## Running the app locally 

(the easy way)
  
### Prerequisites  

You will need both docker and docker-compose to run the app locally. You can download docker from https://www.docker.com/products/docker-desktop/  

- [Docker]  
  
### Running the TTB webapp and backend  
  
1. **Download the zipped file of the repositories and the bootstrap script**  

https://drive.google.com/file/d/1zofsl1du4Uj25ZTYibioYiJhDjtoXY1v/view?usp=sharing

2. **Unzip the file**  

The zipped file contains everything you need, including keys needed*** and the latest code.  Keys are temporary or point to demo/free tier enviroments (postgres on Vercel) and I'll destroy them in a few days after the submission. OpenAI keys used have a max tokens credit dollar value of $25 attached to it. 

Zipped file password is `letmein20260203`

3. **Run the application**  
  
 ```bash
 unzip ttb_submission_2026_02_03.zip
 cd Treasury
 sh ttb-docker-compose.sh
 ```  
 
4. **Access the app**  
  Open your browser and navigate to: `http://localhost:3000`  
  
---  
  
## Usage  
 1. Click "Sign In" on the top right corner of the web-app. This will take you directly to the dashboard landing page. No username/password is enforced for this demo.
 2. Navingate on the Dashboard side bar to Compliance --> Label Approvals --> New
 3. Hit the **Create new** button on the top right to create a new labeling job
 4. **Fill out the form** with the product information:  
	  - Enter the Brand Name exactly as it should appear on the label  
	  - Select or enter the Product Class/Type  
	  - Enter the Alcohol Content (e.g., "45" or "45%")  
	  - Enter the Net Contents (e.g., "750 mL")  
 5. **Upload a label image**:  
	 - Click the upload area or drag-and-drop an image  
	  - Supported formats: JPEG, PNG  
	 - For best results, use clear, high-resolution images  
6. **Review results**:  
   - Check the analysis results of the label
   - ✅ Green indicators show matching fields  
   - ❌ Red indicators show mismatches or missing information  
   - Detailed explanations provided for each discrepancy  
   - Approve or Reject the label with a comment  
  
  
## Assumptions & Design Decisions  
  
### Text Matching Logic

The backend supports two configurable analysis modes via the `analysis_mode` parameter:

| Mode | Value | Description |
|------|-------|-------------|
| **OpenAI (Default)** | `using_llm` | Uses GPT for intelligent, context-aware label analysis |
| **Pytesseract** | `pytesseract` | Uses Tesseract OCR for faster, rule-based text verification |

**Case Sensitivity Rules (for pytesseract mode):**
- Brand name, product class, alcohol content, net contents: **case-insensitive** (e.g., "STONE'S THROW" matches "Stone's Throw")
- Government Warning: **ONLY field requiring ALL CAPS** ("GOVERNMENT WARNING" must be exact)

The `analysis_mode` can be set when creating a job (persisted to the database) or overridden during ad-hoc analysis runs (not persisted).

I opted to use OpenAI's LLM (GPT-5.1) as the default because while this exercise is intentionally simplified and could have been accomplished with Tesseract, a more detailed compliance check -- one requiring deeper domain knowledge -- is far better suited for an LLM (with the usual caveats around potential hallucinations etc and the need for thoughtful guardrails).

What I'm proposing here provides the greatest flexibility and extensibility for an AI-powered, complex compliance-approval workflow at the TTB, significantly reducing the human hours required today.
  
### Technical Decisions

- **Configurable Analysis Mode**: The backend supports two analysis modes (`using_llm` and `pytesseract`) that can be configured per job. OpenAI is the default as it provides intelligent, context-aware analysis better suited for complex compliance checks requiring domain knowledge. Pytesseract offers a faster, rule-based alternative using regex pattern matching for scenarios where speed is prioritized over deep semantic understanding.

- **Python/Flask backend**: Implements a clean-architecture (also referred to as hexagonal architecture) code design. The codebase is thoroughly unit tested. And with modern coding-assistance tools like Claude, writing unit tests has become significantly easier and I find unit testing early a meaningful boost to my productivity and development velocity.
  
  
---  
  
## Known Limitations, Trade-offs  
  
1. **Accuracy**: Limited testing with images I grabbed off the internet. In an ideal world, let's suppose we want to ship this to TTB I'd want to back test the results here with historical images approved or rejected from the past. 
2. **Image Quality**: There are no image quality standards enforced. LLMs may be exceptionally good at dealing with poor image quality and low-res images. These are likely not acceptable to the human reviewers.  Only a single label images is supported per submission while in the real world lables, warnings, bottler information etc may span multiple lables on the bottle (front, back etc). 
3. **Security**: The web app currently enforces no authentication or authorization rules. I’ve left some stub code in place to support adding proper authZ/N in the future. No guards against adversarian image inputs. Image sizes aren't capped. 
4. **Efficiency** All images are stored base64 encoded directly in SQL. This is a poor choice at scale.
5. **Concurrency** The webapp (and the backend) provides no guardrails or guarantees around duplicate labels created or one or more reviewers updating the same review jobs. 
  

  
 
## Testing  
  
### Manual Testing  
The application was tested with the following scenarios:  
- ✅ Matching label and form data  
- ✅ Mismatched brand name  
- ✅ Mismatched ABV  
- ✅ Missing fields on label  
- ✅ Low-quality/unreadable image  
  
### Running Unit Tests

cd in to the ttb-pymono:
```bash  
uv run pytest
```  


  

