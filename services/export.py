import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

def generate_trip_pdf(trip_data, form_data, itinerary, trip_name, trip_id):
    """Generate a PDF document for the trip"""
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2E86AB'),
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#A23B72'),
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leading=14
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph(f"🗺️ {trip_name}", title_style))
    story.append(Spacer(1, 20))
    
    # Trip Overview Section
    story.append(Paragraph("📋 Trip Overview", heading_style))
    
    # Create trip details table
    trip_details = [
        ['Destination:', form_data.get('destination', 'N/A')],
        ['Travel Dates:', f"{form_data.get('start_date', 'N/A')} to {form_data.get('end_date', 'N/A')}"],
        ['Duration:', f"{form_data.get('duration', 'N/A')} days"],
        ['Group Size:', f"{form_data.get('group_size', 'N/A')} people"],
        ['Travel Type:', form_data.get('travel_type', 'N/A')],
        ['Budget:', form_data.get('budget', 'N/A')],
        ['Accommodation:', form_data.get('accommodation', 'N/A')],
        ['Season:', form_data.get('season', 'N/A')],
    ]
    
    # Add travel months if available
    travel_months = form_data.get('travel_months', 'N/A')
    if isinstance(travel_months, list):
        travel_months = ', '.join(travel_months)
    trip_details.append(['Travel Months:', travel_months])
    
    # Create table
    table = Table(trip_details, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2E86AB')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Trip Summary
    summary = trip_data.get('trip_summary', '')
    if summary and summary.strip():
        story.append(Paragraph("📝 Trip Summary", heading_style))
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 20))
    
    # Special Requests
    special_requests = form_data.get('special_requests', '').strip()
    if special_requests:
        story.append(Paragraph("✨ Special Requests", heading_style))
        story.append(Paragraph(special_requests, normal_style))
        story.append(Spacer(1, 20))
    
    # Itinerary Section - Use markdown-pdf for better formatting
    if itinerary:
        story.append(Paragraph("🗓️ Detailed Itinerary", heading_style))
        
        # Get itinerary content
        itinerary_content = ""
        if not itinerary.get('demo_mode') and itinerary.get('ai_response'):
            itinerary_content = itinerary['ai_response']
        elif itinerary.get('demo_mode') and itinerary.get('demo_response'):
            itinerary_content = itinerary['demo_response']
        
        if itinerary_content:
            # Process the itinerary content with improved parsing
            try:
                # Clean and process the markdown content
                processed_content = clean_markdown_for_pdf(itinerary_content)
                
                # Extract sections for better organization
                sections = extract_and_format_content_sections(processed_content)
                
                # Process each section
                for section_name, section_content in sections.items():
                    if not section_content.strip():
                        continue
                    
                    lines = section_content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Handle different heading levels
                        if line.startswith('###'):
                            heading_text = re.sub(r'^#+\s*', '', line)
                            # Create a sub-heading style
                            sub_heading_style = ParagraphStyle(
                                'SubHeading',
                                parent=heading_style,
                                fontSize=14,
                                spaceAfter=8,
                                spaceBefore=15,
                                textColor=colors.HexColor('#2E86AB')
                            )
                            story.append(Paragraph(heading_text, sub_heading_style))
                            story.append(Spacer(1, 6))
                        
                        elif line.startswith('##'):
                            heading_text = re.sub(r'^#+\s*', '', line)
                            story.append(Paragraph(heading_text, heading_style))
                            story.append(Spacer(1, 8))
                        
                        elif line.startswith('#'):
                            heading_text = re.sub(r'^#+\s*', '', line)
                            story.append(Paragraph(heading_text, title_style))
                            story.append(Spacer(1, 10))
                        
                        # Handle bullet points with better formatting
                        elif line.startswith('*') or line.startswith('-') or line.startswith('•'):
                            bullet_text = re.sub(r'^[\*\-•]\s*', '', line)
                            
                            # Check if this is a time-based bullet point
                            time_pattern = r'^(\d{1,2}:\d{2}\s*[AP]M)'
                            time_match = re.match(time_pattern, bullet_text)
                            
                            if time_match:
                                # Special formatting for time-based activities
                                time_style = ParagraphStyle(
                                    'TimeStyle',
                                    parent=normal_style,
                                    leftIndent=20,
                                    bulletIndent=10,
                                    spaceAfter=4,
                                    fontSize=10,
                                    textColor=colors.HexColor('#A23B72')
                                )
                                story.append(Paragraph(f"• <b>{bullet_text}</b>", time_style))
                            else:
                                # Regular bullet point
                                bullet_style = ParagraphStyle(
                                    'BulletStyle',
                                    parent=normal_style,
                                    leftIndent=20,
                                    bulletIndent=10,
                                    spaceAfter=4
                                )
                                story.append(Paragraph(f"• {bullet_text}", bullet_style))
                            story.append(Spacer(1, 3))
                        
                        # Handle indented content (sub-bullets)
                        elif line.startswith('    ') or line.startswith('\t'):
                            indented_text = line.lstrip()
                            indented_style = ParagraphStyle(
                                'IndentedStyle',
                                parent=normal_style,
                                leftIndent=40,
                                spaceAfter=3,
                                fontSize=10
                            )
                            story.append(Paragraph(indented_text, indented_style))
                            story.append(Spacer(1, 2))
                        
                        # Regular text
                        else:
                            # Check if line contains links and format accordingly
                            if '<a href=' in line:
                                # Line contains links, use normal style to preserve formatting
                                story.append(Paragraph(line, normal_style))
                            else:
                                story.append(Paragraph(line, normal_style))
                            story.append(Spacer(1, 4))
                        
            except Exception as e:
                # Fallback to simple text if processing fails
                story.append(Paragraph(f"Error processing itinerary: {str(e)}", normal_style))
                # Clean fallback content
                fallback_content = clean_markdown_for_pdf(itinerary_content)
                story.append(Paragraph(fallback_content.replace('\n', '<br/>'), normal_style))
        else:
            story.append(Paragraph("No detailed itinerary available.", normal_style))
    
    # Footer with trip metadata
    story.append(Spacer(1, 30))
    story.append(Paragraph("📋 Trip Information", heading_style))
    
    metadata_table = [
        ['Trip ID:', trip_id],
        ['Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ['Export Format:', 'PDF Document']
    ]
    
    meta_table = Table(metadata_table, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(meta_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def clean_markdown_for_pdf(text):
    """Clean markdown text for PDF generation"""
    if not text:
        return ""
     
    # Convert markdown links to clickable PDF links
    text = convert_markdown_links_to_pdf(text)
    
    # Remove or convert markdown elements that don't work well in PDF
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # Italic
    text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)  # Code
    
    # Handle bullet points better
    text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
    
    # Clean up excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def prepare_markdown_content(content):
    """Prepare markdown content for better PDF rendering"""
    if not content:
        return ""
    
    # Clean up the content
    content = content.strip()
    
    # Ensure content starts with H1 heading for proper hierarchy
    if not content.startswith('#'):
        content = f"# Trip Itinerary\n\n{content}"
    
    # Fix common markdown issues
    # Ensure proper spacing around headers
    content = re.sub(r'\n(#{1,6})', r'\n\n\1', content)
    content = re.sub(r'(#{1,6}.*?)\n([^#\n])', r'\1\n\n\2', content)
    
    # Fix bullet point formatting - convert asterisks to proper markdown bullets
    # Handle inline bullets (like "* 1:30 PM: text")
    content = re.sub(r'\s*\*\s*(\d{1,2}:\d{2}\s*[AP]M)', r'\n\n* **\1**', content)
    
    # Ensure bullet points are on separate lines
    content = re.sub(r'^(\s*)\*\s*', r'\1* ', content, flags=re.MULTILINE)
    
    # Add proper spacing around bullet points
    content = re.sub(r'\n(\s*\*)', r'\n\n\1', content)
    
    # Clean up excessive newlines but preserve intentional breaks
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Ensure the content starts clean
    content = content.lstrip('\n')
    
    return content

def convert_markdown_links_to_pdf(text):
    """Convert markdown links to ReportLab-compatible clickable links"""
    # Pattern to match markdown links: [text](url)
    def link_replacer(match):
        link_text = match.group(1)
        url = match.group(2)
        # Create a clickable link in ReportLab format
        return f'<a href="{url}" color="blue">{link_text}</a>'
    
    # Replace markdown links with ReportLab link format
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', link_replacer, text)
    
    return text

def extract_and_format_content_sections(content):
    """Extract and format different sections of the content for better PDF layout"""
    sections = {}
    current_section = 'main'
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Detect section headers
        if line.startswith('### ') and any(keyword in line.lower() for keyword in ['flight', 'day', 'practical', 'budget', 'seasonal', 'creative']):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            if 'flight' in line.lower():
                current_section = 'flights'
            elif 'day' in line.lower():
                day_match = re.search(r'day\s+(\d+)', line.lower())
                if day_match:
                    current_section = f'day_{day_match.group(1)}'
                else:
                    current_section = 'daily_itinerary'
            elif 'practical' in line.lower():
                current_section = 'practical_tips'
            elif 'budget' in line.lower():
                current_section = 'budget'
            elif 'seasonal' in line.lower():
                current_section = 'seasonal'
            elif 'creative' in line.lower():
                current_section = 'creative'
            else:
                current_section = 'other'
            
            current_content = [line]
        else:
            current_content.append(line)
    
    # Save the last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections