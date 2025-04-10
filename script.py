import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

class InternshalaBot:
    def __init__(self):
        """Initialize the bot with user credentials from environment variables"""
        self.email = 'dilipsc570@gmail.com'
        self.password = 'dilip$004'
        
        # Initialize Gemini AI
        genai.configure(api_key='AIzaSyD9tAeFXCHe1-sWsvakCvr35xDHBzXAFj4')
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        if not self.email or not self.password:
            raise ValueError("Email or password not found in environment variables. "
                             "Please set INTERNSHALA_EMAIL and INTERNSHALA_PASSWORD.")
        
        # Setup Chrome options
        options = Options()
        # Uncomment the line below to run in headless mode
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)
        self.actions = ActionChains(self.driver)

    def login(self):
        """Login to Internshala"""
        try:
            print("Logging in to Internshala...")
            self.driver.get("https://internshala.com/login")
            time.sleep(3)  # Wait for page to load
            
            # Wait for login form to load
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            
            # Enter email and password with human-like typing
            self._human_like_typing(email_field, self.email)
            self._human_like_typing(password_field, self.password)
            
            # Submit the form
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login_submit")))
            self._human_like_click(login_button)
            
            # Wait for successful login
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "profile_container")))
            print("Login successful!")
            return True
        except TimeoutException:
            print("Login failed. Please check your credentials.")
            return False
        except Exception as e:
            print(f"An error occurred during login: {e}")
            return False

    def search_internships(self, keywords):
        """Search for internships based on given keywords"""
        try:
            print(f"Searching for internships with keywords: {keywords}")
            
            # Build the search URL
            search_url = f"https://internshala.com/internships/{keywords.replace(' ', '-')}-internship"
            print(f"Search URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Wait for search results to load
            try:
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "internship_meta")))
                print(f"Found internships for: {keywords}")
                return True
            except TimeoutException:
                print("No internships found or page didn't load properly")
                return False
                
        except Exception as e:
            print(f"Error searching for internships: {e}")
            return False

    def get_all_internships_on_page(self):
        """Get all internship listings on the current page"""
        try:
            # Wait for internships to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "individual_internship")))
            
            # Get all internship containers
            all_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.individual_internship")
            
            # Filter out training course cards
            valid_internships = []
            for container in all_containers:
                try:
                    # Check for training course URL
                    try:
                        apply_button = container.find_element(By.CSS_SELECTOR, ".apply-now-cta")
                        href = apply_button.get_attribute("href")
                        if href and "trainings.internshala.com" in href:
                            print("Skipping training course listing")
                            continue
                    except:
                        pass
                    
                    # Check if it's a training course card
                    heading = container.find_element(By.CSS_SELECTOR, ".heading_paragraph").text.lower()
                    if "get hired" in heading or "training" in heading or "course" in heading:
                        print(f"Skipping training course: {heading}")
                        continue
                    
                    # Check for course fees section
                    try:
                        container.find_element(By.CSS_SELECTOR, ".fees-section")
                        print("Skipping paid course listing")
                        continue
                    except:
                        pass
                    
                    valid_internships.append(container)
                except:
                    # If we can't check the heading, assume it's a valid internship
                    valid_internships.append(container)
            
            if not valid_internships:
                print("No valid internships found on the page")
                return []
            
            print(f"Found {len(valid_internships)} valid internships out of {len(all_containers)} total listings")
            return valid_internships
        except Exception as e:
            print(f"Error getting internship listings: {e}")
            return []

    def apply_to_internship(self, internship_element):
        """Apply to a specific internship with improved handling"""
        try:
            # Extract internship information
            title_element = internship_element.find_element(By.CSS_SELECTOR, "a.job-title-href")
            internship_title = title_element.text
            
            company_element = internship_element.find_element(By.CSS_SELECTOR, "p.company-name")
            company_name = company_element.text.strip()
            
            # Get stipend information
            try:
                stipend_element = internship_element.find_element(By.CSS_SELECTOR, "span.stipend")
                stipend = stipend_element.text
            except:
                stipend = "Not specified"
            
            print(f"Applying to: {internship_title} at {company_name} (Stipend: {stipend})")
            
            # Store original window handle
            original_window = self.driver.current_window_handle
            
            try:
                # Scroll to the card and click
                self._scroll_into_view(internship_element)
                
                # Try clicking on the title first (more reliable)
                try:
                    self._human_like_click(title_element)
                except:
                    # Fallback to clicking the card
                    self._human_like_click(internship_element)
                    
                print("Clicked on internship listing")
                
                # Wait for new tab or page to load
                time.sleep(3)
                
                # Check if new tab opened
                if len(self.driver.window_handles) > 1:
                    # Switch to the new tab
                    for window_handle in self.driver.window_handles:
                        if window_handle != original_window:
                            self.driver.switch_to.window(window_handle)
                            break
                    print("Switched to new tab")
                
                # Wait for detail page to load
                self._wait_for_page_load()
                
                # Handle any popups
                self._handle_popups()
                
                # Try to find the apply button using various selectors
                apply_button = None
                apply_selectors = [
                    "button#continue_button",
                    "button.btn-primary:contains('Apply now')",
                    "button:contains('Apply')",
                    "a.apply-button",
                    "a:contains('Apply')",
                    ".apply_button",
                    ".apply-now-button",
                    ".apply-now"
                ]
                
                for selector in apply_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and ("apply" in element.text.lower() or "continue" in element.text.lower()):
                                apply_button = element
                                break
                        if apply_button:
                            break
                    except:
                        continue
                
                if not apply_button:
                    # Try a more generic approach - look for any button with "apply" in text
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if button.is_displayed() and ("apply" in button.text.lower() or "continue" in button.text.lower()):
                            apply_button = button
                            break
                            
                if apply_button:
                    # Scroll to the apply button
                    self._scroll_into_view(apply_button)
                    self._human_like_click(apply_button)
                    print("Clicked Apply button")
                    
                    # Wait for application form to load
                    time.sleep(3)
                    self._wait_for_page_load()
                    
                    # Handle application form
                    if self._handle_application_form():
                        print(f"Successfully applied to: {internship_title}")
                        
                        # After application, close current tab if it's not the original
                        if len(self.driver.window_handles) > 1 and self.driver.current_window_handle != original_window:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            print("Closed application tab and returned to search results")
                            
                        return True
                    else:
                        print(f"Failed to complete application for: {internship_title}")
                        
                        # Close current tab if it's not the original
                        if len(self.driver.window_handles) > 1 and self.driver.current_window_handle != original_window:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                        
                        return False
                else:
                    print("Could not find Apply button")
                    
                    # Close current tab if it's not the original
                    if len(self.driver.window_handles) > 1 and self.driver.current_window_handle != original_window:
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                        
                    return False
                    
            except Exception as e:
                print(f"Error during application process: {e}")
                
                # Make sure we return to the original window
                try:
                    if len(self.driver.window_handles) > 1 and self.driver.current_window_handle != original_window:
                        self.driver.close()
                        self.driver.switch_to.window(original_window)
                except:
                    pass
                    
                return False
                    
        except Exception as e:
            print(f"Error applying to internship: {e}")
            return False

    def _scroll_into_view(self, element):
        """Scroll element into center of view with smooth scrolling"""
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", 
                element
            )
            time.sleep(0.5)  # Small pause for scroll to complete
        except Exception as e:
            print(f"Error scrolling to element: {e}")

    def _wait_for_page_load(self):
        """Wait for page to fully load"""
        try:
            self.driver.execute_script("return document.readyState") == "complete"
            # Wait for any AJAX calls to complete
            time.sleep(2)
        except Exception as e:
            print(f"Error waiting for page load: {e}")
            time.sleep(3)  # Fallback wait
            
    def _handle_popups(self):
        """Handle any popups that might interfere with the application process"""
        try:
            # Check for common popup close buttons but don't click them
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                ".modal-close, .close-btn, button.close, .popup-close, .modal .close, [aria-label='Close']")
            
            # Just log if popups are found, don't close them
            if close_buttons:
                print("Found popup elements, but not closing them")
                
        except Exception as e:
            print(f"Error checking for popups: {e}")

    def _analyze_form_field(self, field):
        """Use Gemini AI to analyze and determine the best value for a form field"""
        try:
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name")
            field_id = field.get_attribute("id")
            field_label = field.get_attribute("aria-label") or field.get_attribute("placeholder") or ""
            
            # Create a prompt for Gemini AI
            prompt = f"""
            Analyze this form field and suggest the best value to fill:
            Field Type: {field_type}
            Field Name: {field_name}
            Field ID: {field_id}
            Field Label: {field_label}
            
            Available options (if any): {[option.text for option in field.find_elements(By.TAG_NAME, "option")] if field_type == "select" else "N/A"}
            
            User Information:
            - Name: Dilip S Chakravarthi
            - Email: {self.email}
            - Phone: +917975077029
            - GitHub: https://github.com/DilipSC
            - LinkedIn: https://www.linkedin.com/in/dilip-s-chakravarthi-5656ab209/
            - Portfolio: https://dilip-dev.vercel.app/
            
            Return the most appropriate value to fill in this field.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error analyzing field with Gemini AI: {e}")
            return None

    def _handle_application_form(self):
        """Handle the application form with comprehensive field detection and filling"""
        try:
            # Wait for form to load completely
            self._wait_for_page_load()
            
            # Handle any popups
            self._handle_popups()
            
            # First handle the cover letter field with specific structure
            try:
                # Try to find the cover letter container
                cover_letter_container = self.driver.find_element(By.CSS_SELECTOR, ".cover_letter_container.application_modal")
                if cover_letter_container.is_displayed():
                    # Try to find the textarea
                    try:
                        textarea = cover_letter_container.find_element(By.ID, "cover_letter")
                        if textarea.is_displayed():
                            self._scroll_into_view(textarea)
                            response = self._generate_cover_letter_for_role()
                            self._human_like_typing(textarea, response)
                            print("Filled cover letter field")
                    except:
                        # If textarea not found, try the rich text editor
                        try:
                            rich_editor = cover_letter_container.find_element(By.CSS_SELECTOR, ".ql-editor")
                            if rich_editor.is_displayed():
                                self._scroll_into_view(rich_editor)
                                response = self._generate_cover_letter_for_role()
                                # For rich text editor, we need to use JavaScript to set the content
                                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", rich_editor, f"<p>{response}</p>")
                                print("Filled cover letter rich text editor")
                        except:
                            print("Could not find textarea or rich text editor in cover letter container")
            except Exception as e:
                print(f"Error handling cover letter field: {e}")
            
            # Handle the common "Why should you be hired" field with specific structure
            try:
                # Try to find the field using the specific structure
                assessment_question = self.driver.find_element(By.XPATH, "//div[contains(@class, 'assessment_question')]//label[contains(text(), 'Why should you be hired')]")
                if assessment_question.is_displayed():
                    # Find the associated textarea
                    try:
                        # First try to find the textarea directly
                        textarea = self.driver.find_element(By.ID, "cover_letter")
                        if textarea.is_displayed():
                            self._scroll_into_view(textarea)
                            response = self._generate_cover_letter_for_role()
                            self._human_like_typing(textarea, response)
                            print("Filled 'Why should you be hired' field")
                    except:
                        # If direct textarea not found, try the rich text editor
                        try:
                            rich_editor = self.driver.find_element(By.CSS_SELECTOR, ".ql-editor")
                            if rich_editor.is_displayed():
                                self._scroll_into_view(rich_editor)
                                response = self._generate_cover_letter_for_role()
                                # For rich text editor, we need to use JavaScript to set the content
                                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", rich_editor, f"<p>{response}</p>")
                                print("Filled 'Why should you be hired' rich text editor")
                        except:
                            print("Could not find textarea or rich text editor for 'Why should you be hired' field")
            except Exception as e:
                print(f"Error handling 'Why should you be hired' field: {e}")
            
            # Handle other cover letter or "Why should you be hired" fields using various selectors
            try:
                textarea_selectors = [
                    "textarea[placeholder*='Mention in detail what relevant skill']",
                    "textarea[placeholder*='Why should you be hired']",
                    "textarea[placeholder*='Cover letter']",
                    "textarea[placeholder*='Tell us why you should be hired']",
                    "textarea[placeholder*='Why should we hire you']"
                ]
                
                for selector in textarea_selectors:
                    try:
                        textarea = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if textarea.is_displayed() and textarea.get_attribute("value") == "":
                            self._scroll_into_view(textarea)
                            response = self._generate_cover_letter_for_role()
                            self._human_like_typing(textarea, response)
                            print("Filled cover letter/Why should you be hired field")
                            break
                    except:
                        continue
                
                # Also try to find by label text
                try:
                    textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    for textarea in textareas:
                        try:
                            # Try to find associated label
                            field_id = textarea.get_attribute("id")
                            if field_id:
                                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                                label_text = label.text.strip().lower()
                                
                                if any(keyword in label_text for keyword in ["cover letter", "why should you be hired", "why hire you", "why should we hire you"]):
                                    if textarea.is_displayed() and textarea.get_attribute("value") == "":
                                        self._scroll_into_view(textarea)
                                        response = self._generate_cover_letter_for_role()
                                        self._human_like_typing(textarea, response)
                                        print(f"Filled field with label: {label_text}")
                                        break
                        except:
                            continue
                except:
                    pass
                    
            except Exception as e:
                print(f"Error handling cover letter field: {e}")
            
            # Handle radio buttons for availability
            try:
                # Find and select "Yes, I am available to join immediately"
                immediate_availability = self.driver.find_element(By.XPATH, "//input[@type='radio' and following-sibling::text()[contains(., 'Yes, I am available')]]")
                if not immediate_availability.is_selected():
                    self._scroll_into_view(immediate_availability)
                    self._human_like_click(immediate_availability)
                    print("Selected immediate availability")
            except Exception as e:
                # Alternative way to find radio buttons
                try:
                    radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radio_buttons and len(radio_buttons) > 0:
                        self._scroll_into_view(radio_buttons[0])
                        self._human_like_click(radio_buttons[0])
                        print("Selected first available radio button")
                except Exception as e2:
                    print(f"Could not select radio button: {e2}")
            
            # Find and fill all other visible input and textarea fields
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
            for field in input_fields:
                try:
                    if field.is_displayed() and field.get_attribute("value") == "":
                        self._scroll_into_view(field)
                        
                        # Skip if it's a file upload field
                        if field.get_attribute("type") == "file":
                            continue
                        
                        # Try to find the associated label
                        label_text = ""
                        try:
                            # Try to find label using for attribute
                            field_id = field.get_attribute("id")
                            if field_id:
                                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                                label_text = label.text.strip()
                            
                            # If no label found with for attribute, try to find nearby label
                            if not label_text:
                                label = field.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form-group') or contains(@class, 'custom-question')]//label")
                                label_text = label.text.strip()
                        except:
                            # If no label found, try to get placeholder as fallback
                            label_text = field.get_attribute("placeholder") or ""
                        
                        # Skip if this is a cover letter or "Why should you be hired" field (already handled)
                        if any(keyword in label_text.lower() for keyword in ["cover letter", "why should you be hired", "why hire you", "why should we hire you"]):
                            continue
                        
                        # Generate appropriate response based on label text
                        response = self._get_appropriate_field_response(label_text)
                        self._human_like_typing(field, response)
                        print(f"Filled field with label: {label_text}")
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Error filling field: {e}")
                    continue
            
            # Handle custom questions that might appear
            custom_questions = self.driver.find_elements(By.CSS_SELECTOR, ".custom-question textarea, .custom-question input[type='text']")
            for question_field in custom_questions:
                try:
                    if question_field.is_displayed() and question_field.get_attribute("value") == "":
                        self._scroll_into_view(question_field)
                        
                        # Try to find the question text from label
                        question_text = ""
                        try:
                            # Try to find label using for attribute
                            field_id = question_field.get_attribute("id")
                            if field_id:
                                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                                question_text = label.text.strip()
                            
                            # If no label found with for attribute, try to find nearby label
                            if not question_text:
                                label = question_field.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form-group') or contains(@class, 'custom-question')]//label")
                                question_text = label.text.strip()
                        except:
                            question_text = "Custom question"
                        
                        # Skip if this is a cover letter or "Why should you be hired" field (already handled)
                        if any(keyword in question_text.lower() for keyword in ["cover letter", "why should you be hired", "why hire you", "why should we hire you"]):
                            continue
                        
                        # Generate answer based on question
                        answer = self._generate_answer_for_question(question_text)
                        self._human_like_typing(question_field, answer)
                        print(f"Answered custom question: {question_text}")
                        time.sleep(0.5)
                except Exception as e:
                    print(f"Error handling custom question: {e}")
                    continue
            
            # Submit the form - try multiple selector patterns
            try:
                # Try different selectors for the submit button
                submit_button = None
                selectors = [
                    "button[type='submit']",
                    "input[type='submit']", 
                    ".btn-primary", 
                    ".btn.btn-large[type='submit']",
                    "button:contains('Submit Application')",
                    "button:contains('Submit')"
                ]
                
                for selector in selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button.is_displayed():
                            break
                    except:
                        continue
                
                if not submit_button:
                    # Fallback to any button that might be the submit button
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
                    for button in buttons:
                        if button.is_displayed() and ("submit" in button.text.lower() or "apply" in button.text.lower()):
                            submit_button = button
                            break
                
                if submit_button:
                    # Scroll to the submit button
                    self._scroll_into_view(submit_button)
                    
                    # Click the submit button
                    self._human_like_click(submit_button)
                    print("Clicked submit button")
                    time.sleep(2)
                    return True
                else:
                    print("Could not find any submit button")
                    return False
                    
            except Exception as e:
                print(f"Error submitting form: {e}")
                return False
                
        except Exception as e:
            print(f"Error handling application form: {e}")
            return False

    def _generate_cover_letter_for_role(self):
        """Generate a tailored cover letter based on the current job"""
        try:
            # Get job title and description if available
            job_title = ""
            job_company = ""
            
            try:
                job_title_element = self.driver.find_element(By.CSS_SELECTOR, ".profile_title h4, .job-title")
                job_title = job_title_element.text
            except:
                job_title = "Data Annotation And Preparation For Computer Vision"
                
            try:
                company_element = self.driver.find_element(By.CSS_SELECTOR, ".company_name, .company-name")
                job_company = company_element.text
            except:
                job_company = "Inferigence Quotient Private Limited"
            
            # Use Gemini AI to generate a personalized cover letter
            prompt = f"""
            Write a detailed and specific cover letter for a {job_title} internship at {job_company}.
            The letter should:
            
            1. Be around 250-300 words
            2. Highlight relevant skills in Python, OpenCV, Linux, data annotation, and machine learning
            3. Mention experience with computer vision and data preprocessing
            4. Express genuine interest in the role and the company
            5. Explain why the candidate would be a good fit
            6. Demonstrate strong technical knowledge and passion for the field
            7. Be professional but enthusiastic
            8. Include specific examples of relevant projects or experiences
            
            Don't include generic placeholder text. Make it specific to the role.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except:
                # Fallback cover letter if AI generation fails
                return """
                I'm excited to apply for the Data Annotation and Computer Vision internship at Inferigence Quotient Private Limited. As a Computer Science student with strong Python programming skills and hands-on experience with OpenCV and Linux, I believe I'm well-positioned to contribute effectively to your team.

                My experience includes developing several computer vision projects where I've worked extensively on data annotation, preprocessing, and model training. I've written Python scripts to automate data collection, implemented various preprocessing techniques to enhance image quality, and developed custom annotation tools to streamline the labeling process.

                I'm particularly passionate about computer vision applications and have experience in:
                - Implementing image processing algorithms using OpenCV
                - Developing annotation pipelines for object detection datasets
                - Converting between different annotation formats (COCO, Pascal VOC, YOLO)
                - Training and evaluating machine learning models on annotated datasets

                What excites me most about this internship is the opportunity to work on real-world computer vision problems while learning from experienced professionals in the field. The responsibilities outlined in the job description align perfectly with my technical skills and career goals.

                I'm available to start immediately and eager to contribute to your team's success. I'm a quick learner who thrives in collaborative environments and consistently delivers high-quality work.

                Thank you for considering my application. I look forward to discussing how my skills and enthusiasm can benefit Inferigence Quotient Private Limited.
                """
        except Exception as e:
            print(f"Error generating cover letter: {e}")
            # Return a basic cover letter
            return """
            I'm excited to apply for this internship opportunity. With my strong background in Python programming and data science, I believe I can contribute effectively to your team.
            
            My experience includes working with OpenCV, data annotation, and machine learning projects that required similar skills to those mentioned in your job description. I have hands-on experience with Linux environments and have developed several computer vision applications.
            
            I am particularly interested in this role because it aligns perfectly with my academic background and career aspirations in the field of computer vision and machine learning. The opportunity to work on real-world data annotation and preparation would be invaluable for my professional growth.
            
            I am a quick learner, detail-oriented, and passionate about delivering high-quality work. I am confident that my technical skills in Python, OpenCV, and data preprocessing make me a strong candidate for this position.
            
            Thank you for considering my application. I am available to join immediately and look forward to the opportunity to discuss how I can contribute to your team.
            """

    def _generate_answer_for_question(self, question):
        """Generate an appropriate answer for a custom question"""
        try:
            # Use Gemini AI to generate a response
            prompt = f"""
            Generate a professional and specific answer to this internship application question:
            "{question}"
            
            Context about the applicant:
            - Computer Science student with strong programming skills
            - Experience with Python, OpenCV, and Linux
            - Worked on computer vision and data annotation projects
            - Eager to learn and contribute
            - Available to start immediately
            - Passionate about machine learning and AI
            - Has experience with data preprocessing and annotation
            - Familiar with various computer vision techniques
            - Has worked on multiple projects involving image processing
            
            The answer should be:
            1. 3-5 sentences long
            2. Specific and relevant to the question
            3. Highlight relevant skills and experiences
            4. Professional but enthusiastic
            5. Demonstrate genuine interest in the role
            6. Include specific examples where possible
            7. Show how the skills match the job requirements
            8. Express willingness to learn and contribute
            
            Don't use generic responses. Make it specific to computer vision and data annotation roles.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except:
                # Fallback responses based on common question keywords
                if "why" in question.lower() and "hire" in question.lower():
                    return "My strong technical background in Python and experience with computer vision projects make me an ideal candidate for this role. I have hands-on experience with data annotation and preprocessing, which directly aligns with the key responsibilities. I'm passionate about computer vision applications and eager to contribute to your team while continuing to learn and grow in this specialized field."
                elif "weakness" in question.lower():
                    return "My perfectionism can sometimes lead me to spend extra time refining projects, though I've learned to balance this with meeting deadlines by setting clear milestones. I actively seek feedback to improve and have developed effective time management strategies to ensure high-quality deliverables without unnecessary delays."
                elif "strength" in question.lower():
                    return "My key strength is my ability to quickly learn new technologies and apply them to solve real-world problems. This has enabled me to develop proficiency in Python, OpenCV, and Linux environments. Additionally, I'm highly detail-oriented, which is particularly valuable for data annotation and preparation tasks that require precision and consistency."
                elif "experience" in question.lower():
                    return "I've worked on several computer vision projects where I developed Python scripts for data collection, preprocessing, and annotation. In one project, I created a custom annotation tool that increased labeling efficiency by 30%. I also have experience converting between various annotation formats and integrating preprocessed data into machine learning pipelines."
                else:
                    return "I'm particularly drawn to this opportunity because it perfectly aligns with my technical skills and career interests in computer vision and machine learning. My background in Python programming, experience with OpenCV, and familiarity with Linux environments have prepared me well for the responsibilities outlined in the job description. I'm excited about the prospect of contributing to meaningful projects while learning from experienced professionals in the field."
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I believe my technical skills in Python and experience with data annotation projects make me well-suited for this position. I'm passionate about computer vision and eager to contribute to your team while continuing to develop my skills in this exciting field. I'm available to start immediately and committed to delivering high-quality work."

    def _get_appropriate_field_response(self, placeholder):
        """Return appropriate response based on field placeholder or label"""
        placeholder_lower = placeholder.lower()
        
        # Common fields with specific responses
        if "name" in placeholder_lower:
            return "Dilip S Chakravarthi"
        elif "email" in placeholder_lower:
            return self.email
        elif "phone" in placeholder_lower or "mobile" in placeholder_lower:
            return "+917975077029"
        elif "github" in placeholder_lower:
            return "https://github.com/DilipSC"
        elif "linkedin" in placeholder_lower:
            return "https://www.linkedin.com/in/dilip-s-chakravarthi-5656ab209/"
        elif "portfolio" in placeholder_lower:
            return "https://dilip-dev.vercel.app/"
        elif "college" in placeholder_lower or "university" in placeholder_lower:
            return "Visvesvaraya Technological University"
        elif "degree" in placeholder_lower:
            return "Bachelor of Engineering in Computer Science"
        elif "graduation" in placeholder_lower:
            return "2023"
        elif "location" in placeholder_lower or "address" in placeholder_lower:
            return "Bangalore, Karnataka"
        elif "cover letter" in placeholder_lower:
            return self._generate_cover_letter_for_role()
        elif "why" in placeholder_lower and "hire" in placeholder_lower:
            return "My strong technical background in Python and experience with computer vision projects make me an ideal candidate for this role. I have hands-on experience with data annotation and preprocessing, which directly aligns with the key responsibilities. I'm passionate about computer vision applications and eager to contribute to your team while continuing to learn and grow in this specialized field."
        elif "weakness" in placeholder_lower:
            return "My perfectionism can sometimes lead me to spend extra time refining projects, though I've learned to balance this with meeting deadlines by setting clear milestones. I actively seek feedback to improve and have developed effective time management strategies to ensure high-quality deliverables without unnecessary delays."
        elif "strength" in placeholder_lower:
            return "My key strength is my ability to quickly learn new technologies and apply them to solve real-world problems. This has enabled me to develop proficiency in Python, OpenCV, and Linux environments. Additionally, I'm highly detail-oriented, which is particularly valuable for data annotation and preparation tasks that require precision and consistency."
        elif "experience" in placeholder_lower:
            return "I've worked on several computer vision projects where I developed Python scripts for data collection, preprocessing, and annotation. In one project, I created a custom annotation tool that increased labeling efficiency by 30%. I also have experience converting between various annotation formats and integrating preprocessed data into machine learning pipelines."
        elif "skill" in placeholder_lower:
            return "Python, OpenCV, Linux, Data Annotation, Machine Learning, Computer Vision, Data Preprocessing, Image Processing, Object Detection, Deep Learning"
        elif "project" in placeholder_lower:
            return "Developed a custom annotation tool for computer vision datasets that improved labeling efficiency by 30%. Created Python scripts for automated data collection and preprocessing. Implemented various image processing algorithms using OpenCV for data enhancement."
        elif "interest" in placeholder_lower or "passion" in placeholder_lower:
            return "I'm particularly passionate about computer vision and machine learning applications. I enjoy working on projects that involve data annotation, preprocessing, and model training. The opportunity to work on real-world computer vision problems while learning from experienced professionals excites me."
        elif "availability" in placeholder_lower or "start date" in placeholder_lower:
            return "I am available to start immediately and can commit to the full duration of the internship. I'm flexible with working hours and can adapt to the team's schedule."
        elif "salary" in placeholder_lower or "stipend" in placeholder_lower or "expectation" in placeholder_lower:
            return "I'm flexible with the stipend and more interested in the learning opportunity and experience this internship provides. I'm open to discussing a stipend that aligns with the company's standards and the value I can bring to the team."
        elif "reference" in placeholder_lower:
            return "Available upon request"
        elif "resume" in placeholder_lower or "cv" in placeholder_lower:
            return "I have attached my resume which details my technical skills, projects, and experience in computer vision and machine learning."
        elif "certification" in placeholder_lower:
            return "Python Programming Certification, Machine Learning Fundamentals, Computer Vision Basics"
        elif "language" in placeholder_lower:
            return "English (Fluent), Kannada (Native)"
        elif "achievement" in placeholder_lower:
            return "Developed a custom annotation tool that improved labeling efficiency by 30%. Created multiple computer vision projects that demonstrate my technical skills. Consistently maintained high academic performance throughout my education."
        elif "hobby" in placeholder_lower or "interest" in placeholder_lower:
            return "I enjoy working on personal computer vision projects, contributing to open-source projects, and staying updated with the latest developments in AI and machine learning. I also participate in coding competitions and hackathons."
        else:
            # For fields we can't easily identify, use Gemini AI to generate a response
            return self._generate_answer_for_question(placeholder)

    def _human_like_typing(self, element, text):
        """Type text in a human-like manner"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _human_like_click(self, element):
        """Click an element in a human-like manner"""
        try:
            # Move to element with random delay
            self.actions.move_to_element(element)
            self.actions.pause(random.uniform(0.1, 0.3))
            self.actions.click()
            self.actions.perform()
        except:
            # If click is intercepted, try JavaScript click
            self.driver.execute_script("arguments[0].click();", element)

    def apply_to_all_internships(self, max_applications=10):
        """Apply to all internships on the current page, up to a maximum limit"""
        applied_count = 0
        internships = self.get_all_internships_on_page()
        
        for internship in internships:
            if applied_count >= max_applications:
                print(f"Reached maximum application limit ({max_applications})")
                break
                
            # Random delay to avoid detection
            time.sleep(random.uniform(2, 5))
            
            if self.apply_to_internship(internship):
                applied_count += 1
                
        print(f"Applied to {applied_count} internships")
        return applied_count

    def navigate_to_next_page(self):
        """Navigate to the next page of search results if available"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "a.next")
            if "disabled" not in next_button.get_attribute("class"):
                self._human_like_click(next_button)
                # Wait for the next page to load
                time.sleep(3)
                return True
            else:
                print("No more pages available")
                return False
        except NoSuchElementException:
            print("No next page button found")
            return False
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False

    def close(self):
        """Close the browser and quit the driver"""
        self.driver.quit()
        print("Browser closed")

def main():
    """Main function to run the bot"""
    # List of internship types to search for
    internship_types = [
        "python",
        "data-science",
        "web-development",
        "machine-learning"
    ]
    
    max_applications_per_search = 5
    max_pages_per_search = 2
    
    bot = InternshalaBot()
    
    try:
        # Login to Internshala
        if not bot.login():
            print("Login failed. Exiting.")
            bot.close()
            return
        
        # Process each internship type
        for internship_type in internship_types:
            print(f"\n{'='*50}")
            print(f"Starting search for: {internship_type}")
            print(f"{'='*50}")
            
            # Search for internships
            if not bot.search_internships(internship_type):
                print(f"Failed to search for {internship_type}. Skipping to next type.")
                continue
            
            # Apply to internships across multiple pages
            for page in range(1, max_pages_per_search + 1):
                print(f"\nProcessing page {page} for {internship_type}...")
                bot.apply_to_all_internships(max_applications_per_search)
                
                # Try to navigate to next page, break if no more pages
                if not bot.navigate_to_next_page():
                    break
                    
            print(f"Completed processing for: {internship_type}")
            
        print("\nAutomation completed!")
        
    finally:
        # Always close the browser when done
        bot.close()

if __name__ == "__main__":
    main()