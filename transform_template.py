import re

with open(r'C:\Users\l\OneDrive\Desktop\travel_project\templates\index.html','r',encoding='utf-8') as f:
    html = f.read()

Q = chr(39)
def url(n):
    return "{% url " + Q + n + Q + " %}"

# 1. NAVIGATION
old_btn = '\t\t\t\t\t\t\t\t\t\t<li>\n\t\t\t\t\t\t\t\t\t\t\t<button class="book-btn">立即预订\n\t\t\t\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t\t\t\t</li><!--/.project-btn-->'
new_btn = (
    '\t\t\t\t\t\t\t\t\t\t{% if user.is_authenticated %}'
    '\n\t\t\t\t\t\t\t\t\t\t<li><a href="' + url('my_bookings') + '" class="book-btn">我的预订</a></li>'
    '\n\t\t\t\t\t\t\t\t\t\t<li><a href="' + url('logout') + '" style="color:#fff;padding:12px 15px;display:inline-block;">注销</a></li>'
    '\n\t\t\t\t\t\t\t\t\t\t<li style="color:#ffcc00;padding:14px 10px;">❄ {{ user.username }}</li>'
    '\n\t\t\t\t\t\t\t\t\t\t{% else %}'
    '\n\t\t\t\t\t\t\t\t\t\t<li><a href="' + url('login') + '" style="color:#fff;padding:12px 15px;display:inline-block;">登录</a></li>'
    '\n\t\t\t\t\t\t\t\t\t\t<li><a href="' + url('register') + '" class="book-btn">注册</a></li>'
    '\n\t\t\t\t\t\t\t\t\t\t{% endif %}'
)
html = html.replace(old_btn, new_btn)
print('1 NAV')

# 2. SUBSCRIBE
html = html.replace(
    '<form>',
    '<form action="' + url('subscribe') + '" method="POST">\n\t\t\t\t\t{% csrf_token %}'
)
html = html.replace(
    '<input type="email" class="form-control" placeholder="在此输入您的邮箱地址">',
    '<input type="email" name="email" class="form-control" placeholder="在此输入您的邮箱地址" required>'
)
html = html.replace(
    '<button class="appsLand-btn subscribe-btn">立即订阅</button>',
    '<button type="submit" class="appsLand-btn subscribe-btn">立即订阅</button>'
)
print('2 SUBSCRIBE')

# 3. MESSAGES
msg = '\n\t\t{% if messages %}\n'
msg += '\t\t<div class="container" style="margin-top:90px;">\n'
msg += '\t\t\t{% for message in messages %}\n'
msg += '\t\t\t<div class="alert alert-{{ message.tags }} alert-dismissible fade in" role="alert">\n'
msg += '\t\t\t\t<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\n'
msg += '\t\t\t\t{{ message }}\n\t\t\t</div>\n'
msg += '\t\t\t{% endfor %}\n\t\t</div>\n\t\t{% endif %}'
idx = html.find('<!-- main-menu End -->')
if idx > 0:
    end = html.find('-->', idx) + 3
    html = html[:end] + msg + html[end:]
    print('3 MSG')

# 4. PACKAGES
s = html.find('<!--packages start-->')
e = html.find('<!--packages end-->')
if s > 0 and e > 0:
    pkg_start = html.find('<div class="col-md-4 col-sm-6">', s)
    row_end = html.rfind('</div><!--/.row-->', pkg_start, e) + len('</div><!--/.row-->')
    if pkg_start > 0 and row_end > 0:
        t = '\t\t\t\t\t{% for package in packages %}\n'
        t += '\t\t\t\t\t\t<div class="col-md-4 col-sm-6">\n'
        t += '\t\t\t\t\t\t\t<div class="single-package-item">\n'
        t += '\t\t\t\t\t\t\t\t<img src="{% static package.image_url %}" alt="package-place">\n'
        t += '\t\t\t\t\t\t\t\t<div class="single-package-item-txt">\n'
        t += '\t\t\t\t\t\t\t\t\t<h3>{{ package.name }} <span class="pull-right">${{ package.price|floatformat:0 }}</span></h3>\n'
        t += '\t\t\t\t\t\t\t\t\t<div class="packages-para">\n'
        t += '\t\t\t\t\t\t\t\t\t\t{% for feature in package.feature_list|slice:":2" %}\n'
        t += '\t\t\t\t\t\t\t\t\t\t<p><span><i class="fa fa-angle-right"></i> {{ feature }}</span></p>\n'
        t += '\t\t\t\t\t\t\t\t\t\t{% endfor %}\n'
        t += '\t\t\t\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t\t\t\t\t<div class="packages-review">\n'
        t += '\t\t\t\t\t\t\t\t\t\t<p><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i><i class="fa fa-star"></i>\n'
        t += '\t\t\t\t\t\t\t\t\t\t\t<span>{{ package.review_count }} 条好评</span></p>\n'
        t += '\t\t\t\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t\t\t\t\t<div class="about-btn">\n'
        t += '\t\t\t\t\t\t\t\t\t\t<a href="' + url('package_detail') + ' package.pk %}" class="about-view packages-btn">立即订购</a>\n'
        t += '\t\t\t\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t{% endfor %}'
        html = html[:s] + html[s:pkg_start] + t + '\n\t\t\t\t\t</div><!--/.row-->\n\t\t\t\t</div><!--/.packages-content-->\n\t\t\t</div><!--/.container-->\n\n\t\t</section><!--/.packages-->' + html[e:]
        print('4 PKG')
    else:
        print('4 PKG FAIL')

# 5. TESTIMONIALS
s = html.find('<!-- testemonial Start -->')
e = html.find('<!-- testemonial End -->')
if s > 0 and e > 0:
    cs = html.find('<div class="owl-carousel owl-theme" id="testemonial-carousel">', s)
    ce = html.find('</div><!--/.testemonial-carousel-->', cs) + len('</div><!--/.testemonial-carousel-->')
    if cs > 0 and ce > 0:
        t = '\t\t\t\t<div class="owl-carousel owl-theme" id="testemonial-carousel">\n'
        t += '\t\t\t\t\t{% for testimonial in testimonials %}\n'
        t += '\t\t\t\t\t<div class="home1-testm item">\n'
        t += '\t\t\t\t\t\t<div class="home1-testm-single text-center">\n'
        t += '\t\t\t\t\t\t\t<div class="home1-testm-img"><img src="{% static testimonial.avatar_url %}" alt="img"/></div>\n'
        t += '\t\t\t\t\t\t\t<div class="home1-testm-txt">\n'
        t += '\t\t\t\t\t\t\t\t<span class="icon section-icon"><i class="fa fa-quote-left" aria-hidden="true"></i></span>\n'
        t += '\t\t\t\t\t\t\t\t<p>{{ testimonial.quote }}</p>\n'
        t += '\t\t\t\t\t\t\t\t<h3><a href="#">{{ testimonial.guest_name }}</a></h3>\n'
        t += '\t\t\t\t\t\t\t\t<h4>{{ testimonial.location }}</h4>\n'
        t += '\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t{% endfor %}\n\t\t\t\t</div><!--/.testemonial-carousel-->'
        html = html[:cs] + t + html[ce:]
        print('5 TEST')
    else:
        print('5 TEST FAIL')

# 6. BLOG
s = html.find('<!--blog start-->')
e = html.find('<!--blog end-->')
if s > 0 and e > 0:
    row_s = html.find('<div class="row">', s)
    last = row_s; last_e = last
    while True:
        p = html.find('</div><!--/.row-->', last)
        if p < 0 or p > e: break
        last_e = p + len('</div><!--/.row-->'); last = p + 1
    if row_s > 0 and last_e > row_s:
        t = '\t\t\t\t\t\t\t<div class="row">\n'
        t += '\t\t\t\t\t\t\t\t{% for post in blog_posts %}\n'
        t += '\t\t\t\t\t\t\t\t<div class="col-sm-4 col-md-4">\n'
        t += '\t\t\t\t\t\t\t\t\t<div class="thumbnail">\n'
        t += '\t\t\t\t\t\t\t\t\t\t<h2>探索足迹 <span>{{ post.published_date|date:"d F Y" }}</span></h2>\n'
        t += '\t\t\t\t\t\t\t\t\t\t<div class="thumbnail-img"><img src="{% static post.image_url %}" alt="blog-img"><div class="thumbnail-img-overlay"></div></div>\n'
        t += '\t\t\t\t\t\t\t\t\t\t<div class="caption"><div class="blog-txt">\n'
        t += '\t\t\t\t\t\t\t\t\t\t\t<h3><a href="' + url('blog_detail') + ' post.pk %}">{{ post.title }}</a></h3>\n'
        t += '\t\t\t\t\t\t\t\t\t\t\t<p>{{ post.excerpt }}</p>\n'
        t += '\t\t\t\t\t\t\t\t\t\t\t<a href="' + url('blog_detail') + ' post.pk %}">阅读全文</a>\n'
        t += '\t\t\t\t\t\t\t\t\t\t</div></div>\n\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t\t\t\t{% endfor %}\n\t\t\t\t\t\t\t</div><!--/.row-->'
        html = html[:row_s] + t + html[last_e:]
        print('6 BLOG')
    else:
        print('6 BLOG FAIL')

# 7. GALLERY
s = html.find('<!--gallery start-->')
e = html.find('<!--gallery end-->')
if s > 0 and e > 0:
    row_s = html.find('<div class="row">', s)
    last = row_s; last_e = last
    while True:
        p = html.find('</div><!--/.row-->', last)
        if p < 0 or p > e: break
        last_e = p + len('</div><!--/.row-->'); last = p + 1
    if row_s > 0 and last_e > row_s:
        t = '\t\t\t\t\t<div class="row">\n'
        t += '\t\t\t\t\t\t{% for destination in destinations %}\n'
        t += '\t\t\t\t\t\t<div class="col-sm-3">\n'
        t += '\t\t\t\t\t\t\t<div class="single-gallery-item">\n'
        t += '\t\t\t\t\t\t\t\t<img src="{% static destination.image_url %}" alt="{{ destination.name }}">\n'
        t += '\t\t\t\t\t\t\t\t<div class="single-gallery-item-txt">\n'
        t += '\t\t\t\t\t\t\t\t\t<h4><a href="#">{{ destination.name }}</a></h4>\n'
        t += '\t\t\t\t\t\t\t\t\t<h3>{{ destination.country }} <br> {{ destination.city }}</h3>\n'
        t += '\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t</div>\n'
        t += '\t\t\t\t\t\t{% endfor %}\n\t\t\t\t\t</div><!--/.row-->'
        html = html[:row_s] + t + html[last_e:]
        print('7 GALLERY')
    else:
        print('7 GALLERY FAIL')

# 8. SPECIAL OFFERS
if '<h2>神秘泰兰德风情游</h2>' in html:
    html = html.replace('<h2>神秘泰兰德风情游</h2>', '<h2>{{ offer.title }}</h2>', 1)
    html = html.replace('6.0折', '{{ offer.discount }}%折')
    html = html.replace('$999', '${{ offer.price|floatformat:0 }}')
    html = html.replace('$ 1450', '$ {{ offer.original_price|floatformat:0 }}')
    desc = '享受最纯正的阳光沙滩与热带风情，这条全包式独家度假路线将为您扫清一切出游烦恼。现在两人成团即可立享专属优惠加成。'
    html = html.replace(desc, '{{ offer.description }}')
    old_f = '\t\t\t\t\t\t\t\t\t\t<p>\n\t\t\t\t\t\t\t\t\t\t\t<span>\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-angle-right"></i> 5 天 6 晚\n\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t<span>\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-angle-right"></i> 2 人同行\n\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t<span>\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-angle-right"></i> 入住五星级高奢酒店\n\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t</p>\n\t\t\t\t\t\t\t\t\t\t<p>\n\t\t\t\t\t\t\t\t\t\t\t<span>\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-angle-right"></i> 机场专属接送接驳\n\t\t\t\t\t\t\t\t\t\t\t</span>\n\t\t\t\t\t\t\t\t\t\t\t<span>\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-angle-right"></i> 赠送海鲜饕餮大餐\n\t\t\t\t\t\t\t\t\t\t\t</span>  \n\t\t\t\t\t\t\t\t\t\t</p>'
    new_f = '\t\t\t\t\t\t\t\t\t\t{% for feature in offer.feature_list %}\n'
    new_f += '\t\t\t\t\t\t\t\t\t\t<p><span><i class="fa fa-angle-right"></i> {{ feature }}</span></p>\n'
    new_f += '\t\t\t\t\t\t\t\t\t\t{% endfor %}'
    html = html.replace(old_f, new_f)
    html = html.replace(
        'class="special-offer-content">\n\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t<div class="col-sm-8">',
        'class="special-offer-content">\n\t\t\t\t\t{% for offer in special_offers %}\n\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t<div class="col-sm-8">'
    )
    html = html.replace(
        '</div><!--/.special-offer-content-->',
        '\t\t\t\t\t{% endfor %}\n\t\t\t\t\t</div><!--/.special-offer-content-->'
    )
    print('8 OFFERS')
else:
    print('8 OFFERS FAIL')

# 9. SEARCH BUTTONS type=submit
html = html.replace(
    'class="about-view travel-btn">\n\t\t\t\t\t\t\t\t\t\t\t搜索路线',
    'type="submit" class="about-view travel-btn">\n\t\t\t\t\t\t\t\t\t\t\t搜索路线'
)
html = html.replace(
    'class="about-view travel-btn">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t搜索酒店',
    'type="submit" class="about-view travel-btn">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t搜索酒店'
)
print('9 BTN')

# 10. TOUR TAB FORM
html = html.replace(
    '\t\t\t\t\t\t\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="col-lg-4 col-md-4 col-sm-12">',
    '\t\t\t\t\t\t\t\t\t\t<form action="' + url('search') + '" method="GET">\n\t\t\t\t\t\t\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="col-lg-4 col-md-4 col-sm-12">',
    1
)
html = html.replace(
    '\t\t\t\t\t\t\t\t\t</div><!--/.tab-para-->\n\n\t\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->\n\n\t\t\t\t\t\t\t\t\t<div role="tabpanel" class="tab-pane fade in" id="hotels">',
    '\t\t\t\t\t\t\t\t\t</form>\n\t\t\t\t\t\t\t\t\t</div><!--/.tab-para-->\n\n\t\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->\n\n\t\t\t\t\t\t\t\t\t<div role="tabpanel" class="tab-pane fade in" id="hotels">',
    1
)

# 11. HOTEL TAB FORM
html = html.replace(
    '\t\t\t\t\t\t\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="col-lg-4 col-md-4 col-sm-12">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<div class="single-tab-select-box">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<h2>目的地酒店</h2>',
    '\t\t\t\t\t\t\t<form action="' + url('hotel_list') + '" method="GET">\n\t\t\t\t\t\t\t\t\t\t\t<div class="row">\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="col-lg-4 col-md-4 col-sm-12">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<div class="single-tab-select-box">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<h2>目的地酒店</h2>',
    1
)
html = html.replace(
    '\t\t\t\t\t\t\t\t\t\t</div><!--/.tab-para-->\n\n\t\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->\n\n\t\t\t\t\t\t\t\t\t<div role="tabpanel" class="tab-pane fade in" id="flights">',
    '\t\t\t\t\t\t\t</form>\n\t\t\t\t\t\t\t\t\t\t</div><!--/.tab-para-->\n\n\t\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->\n\n\t\t\t\t\t\t\t\t\t<div role="tabpanel" class="tab-pane fade in" id="flights">',
    1
)

# 12. FLIGHT TAB FORM
html = html.replace(
    '\t\t\t\t\t\t\t\t\t\t\t<h2>出发城市</h2>',
    '\t\t\t\t\t\t\t\t<form action="' + url('flight_list') + '" method="GET">\n\t\t\t\t\t\t\t\t\t\t\t<h2>出发城市</h2>',
    1
)
# Close flight form
idx = html.rfind('\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->')
if idx > 0:
    html = html[:idx] + '\t\t\t\t\t\t\t\t\t</form>\n\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->' + html[idx + len('\t\t\t\t\t\t\t\t</div><!--/.tabpannel-->'):]
print('10-12 FORMS')

with open(r'C:\Users\l\OneDrive\Desktop\travel_project\templates\index.html','w',encoding='utf-8') as f:
    f.write(html)
print('SAVED')
print('DONE ALL')
