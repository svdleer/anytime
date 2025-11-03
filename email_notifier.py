"""
Email notification module for booking confirmations.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from config import Config

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for booking events."""
    
    @staticmethod
    def send_booking_success(lesson_name: str, lesson_time: datetime, instructor: str = "") -> bool:
        """
        Send email notification when a lesson is successfully booked.
        
        Args:
            lesson_name: Name of the lesson
            lesson_time: Start time of the lesson
            instructor: Name of the instructor (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not Config.ENABLE_EMAIL:
            logger.debug("Email notifications disabled")
            return False
        
        if not Config.EMAIL_FROM or not Config.EMAIL_TO:
            logger.warning("Email not configured. Set EMAIL_FROM and EMAIL_TO in .env")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'✅ Les geboekt: {lesson_name}'
            msg['From'] = f'Hetty - Sportivity Assistente <{Config.EMAIL_FROM}>'
            msg['To'] = Config.EMAIL_TO
            
            # Format lesson time
            lesson_date = lesson_time.strftime('%A, %B %d, %Y')
            lesson_hour = lesson_time.strftime('%H:%M')
            
            # Plain text version
            text_body = f"""
Sportivity Boeking Bevestigd!

Les: {lesson_name}
Datum: {lesson_date}
Tijd: {lesson_hour}
{'Instructeur: ' + instructor if instructor else ''}

Locatie: First Class Sports

Deze boeking is automatisch gemaakt door uw zwaar illegale Sportivity reserverings assistente Hetty.

Controleer de Sportivity app om te bevestigen of wijzigingen aan te brengen.
"""
            
            # HTML version - Modern Dutch design
            html_body = f"""
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #f7AA0f 0%, #ff8c00 100%); padding: 40px 20px; text-align: center;">
            <div style="background-color: rgba(255,255,255,0.2); border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 48px;">🏋️</span>
            </div>
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 600;">Boeking Bevestigd!</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0; font-size: 16px;">Je les is gereserveerd ✅</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #333; margin: 0 0 25px; font-size: 20px; font-weight: 600;">Les Details</h2>
            
            <!-- Lesson Info Card -->
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="margin-bottom: 18px;">
                    <div style="color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Les</div>
                    <div style="color: #333; font-size: 20px; font-weight: 600;">{lesson_name}</div>
                </div>
                
                <div style="display: flex; gap: 20px; margin-bottom: 18px;">
                    <div style="flex: 1;">
                        <div style="color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">📅 Datum</div>
                        <div style="color: #333; font-size: 15px; font-weight: 500;">{lesson_date}</div>
                    </div>
                    <div style="flex: 1;">
                        <div style="color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">🕐 Tijd</div>
                        <div style="color: #333; font-size: 15px; font-weight: 500;">{lesson_hour}</div>
                    </div>
                </div>
                
                {'<div style="margin-bottom: 18px;"><div style="color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">👤 Instructeur</div><div style="color: #333; font-size: 15px; font-weight: 500;">' + instructor + '</div></div>' if instructor else ''}
                
                <div>
                    <div style="color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">📍 Locatie</div>
                    <div style="color: #333; font-size: 15px; font-weight: 500;">First Class Sports</div>
                </div>
            </div>
            
            <!-- Info Box -->
            <div style="background-color: #fff3cd; border-left: 4px solid #f7AA0f; padding: 15px 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                    <strong>🤖 Automatisch gereserveerd</strong><br>
                    Deze boeking is gemaakt door <em>uw zwaar illegale Sportivity reserverings assistente Hetty</em>.
                </p>
            </div>
            
            <!-- Action Button -->
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://www.sportivity.com" style="display: inline-block; background: linear-gradient(135deg, #f7AA0f 0%, #ff8c00 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 25px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 12px rgba(247,170,15,0.3);">
                    Open Sportivity App
                </a>
            </div>
            
            <p style="color: #999; font-size: 13px; text-align: center; margin: 20px 0 0; line-height: 1.6;">
                Controleer de Sportivity app om je boeking te bevestigen of wijzigingen aan te brengen.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #2d3436; color: #b2bec3; padding: 25px 30px; text-align: center;">
            <p style="margin: 0 0 8px; font-size: 13px; font-weight: 500;">
                Uw zwaar illegale Sportivity reserverings assistente Hetty
            </p>
            <p style="margin: 0; font-size: 12px; opacity: 0.7;">
                © {datetime.now().strftime('%Y')} | Altijd op tijd, nooit te laat
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            logger.info(f"Sending booking confirmation email for {lesson_name}")
            
            # Use SSL for port 465, TLS for port 587
            if Config.EMAIL_SMTP_PORT == 465:
                # SSL connection
                with smtplib.SMTP_SSL(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT) as server:
                    if Config.EMAIL_SMTP_USER and Config.EMAIL_SMTP_PASSWORD:
                        server.login(Config.EMAIL_SMTP_USER, Config.EMAIL_SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                # TLS connection (port 587)
                with smtplib.SMTP(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT) as server:
                    server.starttls()
                    if Config.EMAIL_SMTP_USER and Config.EMAIL_SMTP_PASSWORD:
                        server.login(Config.EMAIL_SMTP_USER, Config.EMAIL_SMTP_PASSWORD)
                    server.send_message(msg)
            
            logger.info(f"✓ Email sent successfully to {Config.EMAIL_TO}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}", exc_info=True)
            return False
    
    @staticmethod
    def send_retry_notification(lesson_name: str, lesson_time: datetime, attempts: int) -> bool:
        """
        Send notification when retrying to book a full lesson.
        
        Args:
            lesson_name: Name of the lesson
            lesson_time: Start time of the lesson
            attempts: Number of attempts made
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not Config.ENABLE_EMAIL or attempts < 2:  # Only notify after 2+ attempts
            return False
        
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f'⏳ Nog bezig met boeken: {lesson_name}'
            msg['From'] = f'Hetty - Sportivity Assistente <{Config.EMAIL_FROM}>'
            msg['To'] = Config.EMAIL_TO
            
            body = f"""
Sportivity Boeking Update

Hetty probeert nog steeds je les te boeken:

Les: {lesson_name}
Datum: {lesson_time.strftime('%A, %d %B %Y om %H:%M')}
Pogingen: {attempts}

De les zit momenteel vol, maar Hetty blijft de hele dag proberen.

Status: Bezig...
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Use SSL for port 465, TLS for port 587
            if Config.EMAIL_SMTP_PORT == 465:
                with smtplib.SMTP_SSL(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT) as server:
                    if Config.EMAIL_SMTP_USER and Config.EMAIL_SMTP_PASSWORD:
                        server.login(Config.EMAIL_SMTP_USER, Config.EMAIL_SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT) as server:
                    server.starttls()
                    if Config.EMAIL_SMTP_USER and Config.EMAIL_SMTP_PASSWORD:
                        server.login(Config.EMAIL_SMTP_USER, Config.EMAIL_SMTP_PASSWORD)
                    server.send_message(msg)
            
            logger.info(f"✓ Retry notification sent to {Config.EMAIL_TO}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send retry notification: {e}")
            return False
