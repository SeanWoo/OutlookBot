class Email:
    def __init__(self, mail):
        self.mail = mail

        self.date = mail.date
        self.from_as_string = mail.headers["From"]
        self.to_as_string = mail.headers["To"]
        self.subject = mail.headers["Subject"]
        self.to = mail.mail["to"]

        self.body = None

        if len(self.mail.text_html) > 0:
            self.body = "Содержит html содержимое"

        if len(self.mail.text_plain) > 0:
            self.body = self.mail.text_plain[0]

        if len(self.mail.text_not_managed) > 0:
            self.body = self.mail.text_not_managed[0]