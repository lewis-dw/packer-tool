from app.shipper import fedex_class, royal_mail_class, ups_class


fedex = fedex_class.FedEx()
ups = ups_class.UPS()
rm = royal_mail_class.RoyalMail()



rm.update_auth()