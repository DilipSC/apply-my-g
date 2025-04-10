import os
import time
import json
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("internshala_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InternshalaBot:
    def __init__(self, config_file='config.ini'):
        """Initialize the bot with configuration."""
        self.config = self._load_config(config_file)
        self.setup_gemini()
        self.setup_driver()
        self.max_applications = int(self.config['PREFERENCES']['max_applications'])
        
    def _load_config(self, config_file):
        """Load configuration from file."""
        if not os.path.exists(config_file):
            self._create_default_config(config_file)
            
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
    
    def _create_default_config(self, config_file):
        """Create a default configuration file."""
        config = configparser.ConfigParser()
        1
        config['CREDENTIALS'] = {
            'email': 'dilipsc570@gmail.com',
            'password': 'dilip$004'
        }
        
        config['USER_INFO'] = {
            'full_name': 'Dilip',
            'phone': '+917975077029',
            'city': 'Bengaluru',
            'expected_stipend': '10000',
            'resume_path': 'c:/Users/Dilip C/OneDrive/Desktop/Web Dev/ADW/scripttttt/uploads',
            'github': 'https://github.com/DilipSC',
            'linkedin': 'https://www.linkedin.com/in/dilip-s-chakravarthi-5656ab209/',
            'portfolio': 'https://dilip-dev.vercel.app/'
        }
        
        config['PREFERENCES'] = {
            'category': 'web-development',
            'min_stipend': '10000',
            'location': 'work-from-home',  # or specific city, comma-separated for multiple
            'duration': '2',  # in months, use comma for range like "2,3"
            'max_applications': '10'
        }
        
        config['AI'] = {
            'gemini_api_key': 'AIzaSyD9tAeFXCHe1-sWsvakCvr35xDHBzXAFj4'
        }
        
        with open(config_file, 'w') as f:
            config.write(f)
            
        logger.info(f"Created default configuration file at {config_file}. Please edit it with your information.")
        
    def setup_gemini(self):
        """Configure Gemini AI API."""
        try:
            api_key = self.config['AI']['gemini_api_key']
        genai.configure(api_key=api_key)
            
            # Set up the model
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            self.model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            logger.info("Gemini AI API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            raise
            
    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        try:
            chrome_options = Options()
            # Uncomment the line below to run in headless mode (no UI)
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            service = Service()  # Add webdriver path if needed
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def login(self):
        """Log in to Internshala."""
        try:
            logger.info("Logging in to Internshala...")
            self.driver.get("https://internshala.com/login")
            time.sleep(3)  # Wait for page to load
            
            # Find and fill email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.send_keys(self.config['CREDENTIALS']['email'])
            
            # Find and fill password
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.send_keys(self.config['CREDENTIALS']['password'])
            
            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]")))
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url or "home" in self.driver.current_url:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed. Please check your credentials.")
            return False
    
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def search_internships(self):
        """Search for internships based on preferences."""
        try:
            logger.info("Searching for internships...")
            
            # Build the search URL based on preferences
            category = self.config['PREFERENCES']['category']
            min_stipend = self.config['PREFERENCES']['min_stipend']
            location = self.config['PREFERENCES']['location']
            
            # Create the search URL
            search_url = f"https://internshala.com/internships/{category}-internship"
            
            # Add stipend filter if specified
            if min_stipend and min_stipend.strip():
                search_url += f"/stipend-{min_stipend}"
                
            # Add location filter if specified and not work-from-home
            if location and location.strip():
                if location.lower() == "work-from-home":
                    search_url += "/work-from-home-true"
                else:
                    search_url += f"/{location.lower()}-internship"
                    
            logger.info(f"Search URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for results to load
            time.sleep(5)
            
            # Check if there are results
            internships = self.driver.find_elements(By.CLASS_NAME, "individual_internship")
            logger.info(f"Found {len(internships)} internships")
            
            return internships
        except Exception as e:
            logger.error(f"Error searching for internships: {e}")
            return []
            
    def analyze_page_with_gemini(self, html_content, purpose):
        """Use Gemini to analyze HTML content."""
        try:
            if purpose == "identify_fields":
                prompt = f"""
                Analyze this HTML form and identify all the input fields that need to be filled.
                For each field, provide:
                1. The field type (text input, textarea, dropdown, radio, checkbox, etc.)
                2. The field identifier (id, name, or another unique selector)
                3. The expected content type (name, email, phone, cover letter, etc.)
                4. Whether it appears to be required
                
                Return the response as a JSON object that can be parsed programmatically.
                
                HTML content:
                {html_content}
                """
            elif purpose == "analyze_job_description":
                prompt = f"""
                Analyze this job description and extract key information like:
                1. Skills required
                2. Experience level needed
                3. Key responsibilities
                4. Company details
                5. Any specific requirements or questions asked
                
                Also, suggest a personalized response for any "Why should we hire you?" or similar questions,
                focusing on the specific skills and requirements mentioned.
                
                Return the response as a JSON object that can be parsed programmatically.
                
                HTML content:
                {html_content}
                """
                
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Try to extract JSON from the response
            try:
                # If result is wrapped in markdown code blocks, clean it up
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()
                    
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error("Failed to parse Gemini response as JSON")
                logger.debug(f"Raw response: {result}")
                # Fall back to returning the text if JSON parsing fails
                return {"raw_response": result}
                
        except Exception as e:
            logger.error(f"Error using Gemini AI: {e}")
            return {"error": str(e)}
            
    def apply_to_internship(self, internship_element):
        try:
            # Extract internship information for logging
            title_element = internship_element.find_element(By.CSS_SELECTOR, ".job-title-href")
            internship_title = title_element.text
            internship_link = title_element.get_attribute("href")
            
            company_element = internship_element.find_element(By.CSS_SELECTOR, ".company-name")
            company_name = company_element.text
            
            logger.info(f"Applying to: {internship_title} at {company_name}")
            
            # Click on the title to navigate to the details page
            title_element.click()
            logger.info("Clicked on internship title to navigate to details page")
            
            # Wait for page to load completely
            time.sleep(5)
            
            # Find and click the apply button on the details page using multiple strategies
            applied = False
            button_selectors = [
                "#top_easy_apply_button",
                "#easy_apply_button",
                "#mobile_easy_apply_button",
                ".btn.btn-primary.top_apply_now_cta.apply",
                ".btn.btn-large.apply_now_btn",
                "//button[contains(text(), 'Apply now')]",
                "//button[contains(@class, 'apply_now')]",
                "//button[contains(@class, 'apply')]"
            ]

            for selector in button_selectors:
                try:
                    by_method = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                    button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(1)
                    button.click()
                    logger.info(f"Clicked Apply button using selector: {selector}")
                    applied = True
                    time.sleep(3)
                    break
                except Exception as e:
                    logger.debug(f"Could not click button with selector {selector}: {str(e)}")
                    continue

            if not applied:
                for selector in button_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH if selector.startswith('//') else By.CSS_SELECTOR, selector)
                        if elements:
                            self.driver.execute_script("arguments[0].click();", elements[0])
                            logger.info(f"Clicked Apply button using JavaScript and selector: {selector}")
                            applied = True
                            time.sleep(3)
                            break
                    except Exception as e:
                        logger.debug(f"JavaScript click failed for selector {selector}: {str(e)}")
                        continue

            if not applied:
                logger.error("Could not find or click any Apply button on details page")
                return False
                
            # We should now be in the application form
            form_html = self.driver.page_source
            form_analysis = self.analyze_page_with_gemini(form_html, "identify_fields")
            
            # Also analyze the job description to personalize responses
            job_analysis = self.analyze_page_with_gemini(form_html, "analyze_job_description")
            
            logger.info("Form analysis complete. Filling application...")
            
            # Fill the form based on the analysis
            self._fill_application_form(form_analysis, job_analysis)
            
            # Check if there's a submit button and click it if not in test mode
            submit_button_selectors = [
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Apply')]",
                "//input[@type='submit']",
                ".btn.btn-primary[type='submit']",
                "#submitApplicationButton"
            ]

            for selector in submit_button_selectors:
                try:
                    by_method = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                    submit_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    submit_button.click()
                    logger.info(f"Clicked Submit button using selector: {selector}")
                    time.sleep(3)
            return True
        except Exception as e:
                    logger.debug(f"Could not click Submit button with selector {selector}: {str(e)}")
                    continue

            logger.error("Could not find Submit button")
            return False
    
        except Exception as e:
            logger.error(f"Error applying to internship: {e}")
            return False
    
    def _fill_application_form(self, form_analysis, job_analysis):
        """Fill the application form based on AI analysis."""
        try:
            # Get user info from config
            user_info = self.config['USER_INFO']
            
            # Handle different field types
            if 'fields' in form_analysis:
                for field in form_analysis['fields']:
                    field_type = field.get('type', '').lower()
                    field_id = field.get('identifier', '')
                    content_type = field.get('content_type', '').lower()
                    
                    # Skip if we can't identify the field
                    if not field_id:
                        continue
                    
                    # Try to find the element
                    try:
                        # Try different approaches to find the element
                        element = None
                        selectors = [
                            (By.ID, field_id),
                            (By.NAME, field_id),
                            (By.CSS_SELECTOR, field_id)
                        ]
                        
                        for selector_type, selector in selectors:
                            try:
                                element = self.driver.find_element(selector_type, selector)
                                break
                            except NoSuchElementException:
                                continue
                                
                        if element is None:
                            logger.warning(f"Could not find element for {field_id}")
                        continue
                    
                        # Fill based on field type and content type
                        if field_type in ['text', 'textarea', 'email', 'tel', 'input']:
                            # Clear any existing content
                            element.clear()
                            
                            # Determine what to fill in
                            value = ""
                            if 'name' in content_type:
                                value = user_info['full_name']
                            elif 'email' in content_type:
                                value = self.config['CREDENTIALS']['email']
                            elif 'phone' in content_type:
                                value = user_info['phone']
                            elif 'github' in content_type:
                                value = user_info['github']
                            elif 'linkedin' in content_type:
                                value = user_info['linkedin']
                            elif 'portfolio' in content_type:
                                value = user_info['portfolio']
                            elif any(q in content_type for q in ['cover', 'letter', 'why', 'reason']):
                                # Use job analysis to create personalized response
                                if 'suggested_response' in job_analysis:
                                    value = job_analysis['suggested_response']
                                else:
                                    value = self._generate_cover_letter(job_analysis)
                            else:
                                # Default to using field id for matching
                                for key in user_info:
                                    if key.lower() in field_id.lower():
                                        value = user_info[key]
                            break
            
                            # Input the value
                            if value:
                                element.send_keys(value)
                                logger.info(f"Filled {field_id} with {value[:20]}...")
                                
                        elif field_type == 'file' or 'resume' in content_type:
                            # Handle file upload for resume
                            resume_path = os.path.abspath(user_info['resume_path'])
                            if os.path.exists(resume_path):
                                element.send_keys(resume_path)
                                logger.info(f"Uploaded resume from {resume_path}")
                            else:
                                logger.error(f"Resume file not found at {resume_path}")
                                
                        elif field_type in ['select', 'dropdown']:
                            # For dropdown selections, we'd need to handle this differently
                            # This would depend on the specific form structure
                            logger.info(f"Dropdown field {field_id} detected, but not handling complex selects yet")
                            
                        elif field_type in ['checkbox', 'radio']:
                            # Click to select if not already selected
                            if not element.is_selected():
                                element.click()
                                logger.info(f"Selected {field_id}")
                                
                    except Exception as e:
                        logger.error(f"Error filling field {field_id}: {e}")
                        
            else:
                logger.warning("No fields identified in form analysis")
                
        except Exception as e:
            logger.error(f"Error in form filling: {e}")
            
    def _generate_cover_letter(self, job_analysis):
        """Generate a personalized cover letter based on job analysis."""
        try:
            # Extract skills and responsibilities from job analysis
            skills = job_analysis.get('skills', ['web development', 'coding'])
            responsibilities = job_analysis.get('responsibilities', ['developing web applications'])
            
            skills_str = ', '.join(skills[:3])  # Use top 3 skills
            
            # Create a template cover letter
            cover_letter = f"""
            I am excited to apply for this internship opportunity. With my strong background in {skills_str}, 
            I believe I can contribute effectively to your team.
            
            My experience includes working on various projects that required similar skills to those mentioned in your job description. 
            I am particularly interested in {responsibilities[0] if responsibilities else 'this role'} and eager to learn more in this field.
            
            I am a quick learner, detail-oriented, and passionate about delivering high-quality work. 
            I am confident that my technical skills and enthusiasm make me a strong candidate for this position.
            
            Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team.
            """
            
            return cover_letter.strip()
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return "I am excited about this opportunity and believe my skills and passion make me a strong candidate for this position."
            
    def run_application_campaign(self, max_applications=None):
        """Run a campaign to apply for multiple internships."""
        try:
            # Login first
            if not self.login():
                return
                
            # Set maximum applications
            if not max_applications:
                max_applications = int(self.config['PREFERENCES']['max_applications'])
                
            # Search for internships
            internships = self.search_internships()
            
            if not internships:
                logger.info("No internships found matching your criteria")
                return
                
            # Apply to each internship up to the maximum
            applications_submitted = 0
            for i, internship in enumerate(internships):
                if applications_submitted >= max_applications:
                    break
                    
                logger.info(f"Processing internship {i+1}/{len(internships)}")
                
                # Apply to the internship
                success = self.apply_to_internship(internship)
                
                if success:
                    applications_submitted += 1
                    logger.info(f"Successfully applied to internship {i+1}. Total applications: {applications_submitted}/{max_applications}")
                else:
                    logger.warning(f"Failed to apply to internship {i+1}. Continuing to next.")
                    
                # Navigate back to search results if needed
                if "internships" not in self.driver.current_url:
                    self.driver.get(self.driver.current_url.split('?')[0])  # Remove any query parameters
                    time.sleep(3)
                    
            logger.info(f"Application campaign completed. Applied to {applications_submitted} internships.")
            
        except Exception as e:
            logger.error(f"Error in application campaign: {e}")
        finally:
            # Clean up
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources."""
        try:
            self.driver.quit()
            logger.info("WebDriver closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        # Create and run the bot
        bot = InternshalaBot()
        bot.run_application_campaign()
    except Exception as e:
        logger.critical(f"Critical error: {e}")