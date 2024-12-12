
CREATE TABLE countries (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	country_name VARCHAR(64) NOT NULL, 
	country_code VARCHAR(4) NOT NULL, 
	shipping_country_code VARCHAR(4) NOT NULL, 
	etd_required BOOL NOT NULL, 
	sat_indicator BOOL NOT NULL, 
	PRIMARY KEY (id)
)

;

INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (1, 'Albania', 'AL', 'AL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (2, 'Andorra', 'AD', 'AD', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (3, 'Argentina', 'AR', 'AR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (4, 'Australia', 'AU', 'AU', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (5, 'Austria', 'AT', 'AT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (6, 'Azores', 'AZ', 'AZ', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (7, 'Belarus', 'BY', 'BY', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (8, 'Belgium', 'BE', 'BE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (9, 'Bosnia & Herzegovina', 'BA', 'BA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (10, 'Brazil', 'BR', 'BR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (11, 'Bulgaria', 'BG', 'BG', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (12, 'Canada', 'CA', 'CA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (13, 'Ceuta', 'EA', 'EA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (14, 'Chile', 'CL', 'CL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (15, 'China', 'CN', 'CN', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (16, 'Colombia', 'CO', 'CO', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (17, 'Costa Rica', 'CR', 'CR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (18, 'Croatia', 'HR', 'HR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (19, 'Cyprus', 'CY', 'CY', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (20, 'Czech Republic', 'CZ', 'CZ', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (21, 'Denmark', 'DK', 'DK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (22, 'Dominican Republic', 'DO', 'DO', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (23, 'Ecuador', 'EC', 'EC', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (24, 'Estonia', 'EE', 'EE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (25, 'Faroe Islands', 'FO', 'FO', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (26, 'Finland', 'FI', 'FI', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (27, 'France', 'FR', 'FR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (28, 'Germany', 'DE', 'DE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (29, 'Gibraltar', 'GI', 'GI', False, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (30, 'Greece', 'GR', 'GR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (31, 'Greenland', 'GL', 'GL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (32, 'Guam', 'US', 'US', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (33, 'Guatemala', 'GT', 'GT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (34, 'Guernsey', 'GG', 'UK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (35, 'Hong Kong', 'HK', 'HK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (36, 'Hungary', 'HU', 'HU', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (37, 'Iceland', 'IS', 'IS', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (38, 'India', 'IN', 'IN', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (39, 'Indonesia', 'ID', 'ID', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (40, 'Ireland', 'IE', 'IE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (41, 'Israel', 'IL', 'IL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (42, 'Italy', 'IT', 'IT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (43, 'Japan', 'JP', 'JP', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (44, 'Jersey', 'JE', 'UK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (45, 'Kosovo', 'XK', 'XK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (46, 'Latvia', 'LV', 'LV', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (47, 'Liechtenstein', 'LI', 'LI', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (48, 'Lithuania', 'LT', 'LT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (49, 'Luxembourg', 'LU', 'LU', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (50, 'Macedonia', 'MK', 'MK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (51, 'Madeira', 'MD', 'MD', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (52, 'Malaysia', 'MY', 'MY', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (53, 'Malta', 'MT', 'MT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (54, 'Mexico', 'MX', 'MX', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (55, 'Moldova', 'MD', 'MD', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (56, 'Monaco', 'MC', 'MC', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (57, 'Montenegro', 'ME', 'ME', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (58, 'Netherlands', 'NL', 'NL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (59, 'New Zealand', 'NZ', 'NZ', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (60, 'Norway', '0', '0', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (61, 'Panama', 'PA', 'PA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (62, 'Peru', 'PE', 'PE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (63, 'Philippines', 'PH', 'PH', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (64, 'Poland', 'PL', 'PL', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (65, 'Portugal', 'PT', 'PT', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (66, 'Puerto Rico', 'US', 'US', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (67, 'Romania', 'RO', 'RO', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (68, 'Russia', 'RU', 'RU', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (69, 'San Marino', 'SM', 'SM', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (70, 'Serbia', 'RS', 'RS', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (71, 'Singapore', 'SG', 'SG', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (72, 'Slovakia', 'SK', 'SK', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (73, 'Slovenia', 'SI', 'SI', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (74, 'South Africa', 'ZA', 'ZA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (75, 'South Korea', 'KR', 'KR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (76, 'Spain', 'ES', 'ES', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (77, 'Sweden', 'SE', 'SE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (78, 'Switzerland', 'CH', 'CH', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (79, 'Taiwan', 'TW', 'TW', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (80, 'Thailand', 'TH', 'TH', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (81, 'Turkey', 'TR', 'TR', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (82, 'Ukraine', 'UA', 'UA', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (83, 'United Arab Emirates', 'AE', 'AE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (84, 'United Kingdom', 'GB', 'GB', False, True);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (85, 'United States', 'US', 'US', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (86, 'US Virgin Islands', 'VI', 'VI', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (87, 'Uruguay', 'UY', 'UY', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (88, 'Venezuela', 'VE', 'VE', True, False);
INSERT INTO orders (id, country_name, country_code, shipping_country_code, etd_required, sat_indicator) VALUES (89, 'Vietnam', 'VN', 'VN', True, False);