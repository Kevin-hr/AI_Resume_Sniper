from reportlab.pdfgen import canvas

c = canvas.Canvas(r"c:\Users\52648\Documents\02_baijiahao\AI_Resume_Sniper\tests\data\test.pdf")
c.drawString(100, 750, "This is a test PDF file.")
c.save()
