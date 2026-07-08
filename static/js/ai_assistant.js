(function () {
	'use strict';

	var params = new URLSearchParams(window.location.search);
	var trip = {
		country: params.get('country') || '',
		city: params.get('city') || '',
		check_in: params.get('check_in') || '',
		check_out: params.get('check_out') || '',
		days: params.get('days') || '',
		people: params.get('people') || '',
		budget: params.get('budget') || ''
	};

	var destination = trip.city || trip.country || '目的地';
	var routeText = '';
	var routeTitle = document.getElementById('route-title');
	var routeSubtitle = document.getElementById('route-subtitle');
	var assistantStatus = document.getElementById('assistant-status');
	var reasoningCard = document.getElementById('ai-reasoning-card');
	var reasoningContent = document.getElementById('ai-reasoning-content');
	var responseEl = document.getElementById('ai-response');
	var responseContent = document.getElementById('ai-response-content');
	var routeTabs = document.getElementById('route-tabs');
	var loadingEl = document.getElementById('route-loading');
	var errorEl = document.getElementById('ai-error');
	var errorContent = document.getElementById('ai-error-content');
	var hotelStepEl = document.getElementById('hotel-next-step');
	var hotelCardsEl = document.getElementById('hotel-cards');
	var chatLog = document.getElementById('chat-log');
	var chatForm = document.getElementById('chat-form');
	var chatMessage = document.getElementById('chat-message');

	setupPage();
	generateRoute('');

	chatForm.addEventListener('submit', function (event) {
		event.preventDefault();
		var message = chatMessage.value.trim();
		if (!message) return;
		addChat('user', message);
		chatMessage.value = '';
		generateRoute(message);
	});

	routeTabs.addEventListener('click', function (event) {
		var button = event.target.closest('button');
		if (!button) return;
		switchTab(button.dataset.tab || 'overview');
	});

	document.getElementById('reset-route-btn').addEventListener('click', function () {
		generateRoute('请重新生成一版更合理的路线。');
	});

	document.getElementById('save-route-btn').addEventListener('click', function () {
		addChat('assistant', '路线已保存在当前页面，您可以继续修改或选择住宿。');
	});

	document.addEventListener('click', function (event) {
		if (!event.target.classList.contains('save-hotel-btn')) return;
		event.target.textContent = '已加入';
		event.target.disabled = true;
		addChat('assistant', '已把这家住宿加入当前行程草稿。');
	});

	function setupPage() {
		routeTitle.textContent = buildTitle();
		routeSubtitle.textContent = buildSubtitle();
		document.getElementById('trip-summary').innerHTML = buildSummary(trip);
		document.getElementById('destination-map').src = 'https://www.google.com/maps?q=' + encodeURIComponent(destination) + '&output=embed';
		document.getElementById('intro-link').href = 'https://zh.wikipedia.org/wiki/Special:Search?search=' + encodeURIComponent(destination);
	}

	function buildTitle() {
		var title = destination + (trip.days ? trip.days + '日路线' : '路线');
		if (destination === '目的地') title = 'AI 路线规划';
		return title;
	}

	function buildSubtitle() {
		var parts = [];
		if (trip.check_in) parts.push('出发 ' + trip.check_in);
		if (trip.check_out) parts.push('返回 ' + trip.check_out);
		if (trip.people) parts.push(trip.people + '人');
		if (trip.budget) parts.push('预算 ' + trip.budget);
		return parts.join(' · ') || 'AI 将根据您的需求自动安排路线';
	}

	function generateRoute(message) {
		setLoading(true);
		errorEl.style.display = 'none';
		hotelStepEl.style.display = 'none';
		reasoningContent.textContent = '';
		reasoningCard.style.display = 'none';
		responseEl.style.display = 'block';
		responseContent.innerHTML = '';
		setRouteTabs([]);
		assistantStatus.textContent = message ? '正在按你的要求改路线' : '深度思考中';
		if (message) addChat('assistant', '收到，我会基于当前路线重新调整。');

		var payload = Object.assign({}, trip, {
			message: message,
			previous_plan: routeText
		});

		fetch('/api/search/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		}).then(function (response) {
			if (!response.ok) {
				return response.text().then(function (body) {
					throw new Error('服务器错误 (' + response.status + '): ' + body);
				});
			}

			var reader = response.body.getReader();
			var decoder = new TextDecoder();
			var buffer = '';
			routeText = '';

			function processStream() {
				reader.read().then(function (result) {
					if (result.done) return;

					buffer += decoder.decode(result.value, { stream: true });
					var lines = buffer.split('\n');
					buffer = lines.pop();

					lines.forEach(function (rawLine) {
						var line = rawLine.trim();
						if (!line.startsWith('data: ')) return;

						try {
							var data = JSON.parse(line.substring(6));
							if (data.type === 'start') {
								assistantStatus.textContent = '正在规划路线';
							} else if (data.type === 'reasoning') {
								reasoningCard.style.display = 'block';
								reasoningContent.appendChild(document.createTextNode(data.content));
								reasoningContent.scrollTop = reasoningContent.scrollHeight;
							} else if (data.type === 'content') {
								routeText += data.content;
								responseContent.innerHTML = renderRoute(routeText, 'overview');
								responseContent.scrollTop = responseContent.scrollHeight;
							} else if (data.type === 'done') {
								setLoading(false);
								assistantStatus.textContent = '路线已生成';
								addChat('assistant', '路线已更新。你可以继续让我修改，也可以直接选择住宿。');
								setRouteTabs(extractDaySections(routeText));
								showHotelNextStep(routeText);
							} else if (data.type === 'error') {
								showError(data.content);
							}
						} catch (err) {
							// Ignore partial stream lines.
						}
					});

					processStream();
				}).catch(function (err) {
					showError('读取响应时出错：' + err.message);
				});
			}

			processStream();
		}).catch(function (err) {
			showError('请求失败：' + err.message);
		});
	}

	function setLoading(isLoading) {
		loadingEl.style.display = isLoading ? 'block' : 'none';
	}

	function setRouteTabs(daySections) {
		var buttons = [
			'<button class="active" type="button" data-tab="overview">总览</button>',
			'<button type="button" data-tab="pending">待安排</button>'
		];
		daySections.forEach(function (section) {
			buttons.push('<button type="button" data-tab="' + escapeHtml(section.key) + '">' + escapeHtml(section.title) + '</button>');
		});
		routeTabs.innerHTML = buttons.join('');
	}

	function switchTab(tab) {
		Array.prototype.forEach.call(routeTabs.querySelectorAll('button'), function (btn) {
			btn.classList.toggle('active', btn.dataset.tab === tab);
		});
		if (tab === 'pending') {
			responseContent.innerHTML = renderPending();
			return;
		}
		responseContent.innerHTML = renderRoute(routeText, tab);
	}

	function renderPending() {
		return [
			'<div class="pending-card">',
			'<h3>待安排</h3>',
			'<p>这里会放用户下一步确认的内容，例如住宿、交通、门票和餐厅。您也可以直接问 AI：“帮我安排酒店和交通”。</p>',
			'</div>'
		].join('');
	}

	function showError(message) {
		setLoading(false);
		errorEl.style.display = 'block';
		errorContent.textContent = message;
		assistantStatus.textContent = '生成失败';
	}

	function showHotelNextStep(planText) {
		var hotels = buildHotelRecommendations(planText);
		hotelCardsEl.innerHTML = hotels.map(renderHotelCard).join('');
		hotelStepEl.style.display = 'block';
	}

	function buildHotelRecommendations(planText) {
		var nights = Math.max(Number(trip.days || 1) - 1, 1);
		var numbers = (trip.budget.match(/\d+/g) || []).map(function (n) { return Number(n); });
		var maxBudget = numbers.length ? Math.max.apply(null, numbers) : 3000;
		var nightlyBase = Math.max(Math.round(maxBudget / Math.max(nights, 1) * 0.35), 280);
		var areas = guessHotelAreas(destination, planText);
		return [
			{ name: destination + '核心区舒适酒店', area: areas[0], price: Math.round(nightlyBase * 0.85), tags: ['交通方便', '省心'], reason: '适合按每日路线出发，减少跨城通勤。' },
			{ name: destination + '景点附近精品住宿', area: areas[1], price: Math.round(nightlyBase * 1.15), tags: ['近景点', '体验感强'], reason: '适合短天数行程，把更多时间留给游玩。' },
			{ name: destination + '高性价比连锁酒店', area: areas[2], price: Math.round(nightlyBase * 0.65), tags: ['预算友好', '实用'], reason: '适合控制住宿预算，保留餐饮和体验开销。' }
		];
	}

	function guessHotelAreas(baseCity, planText) {
		var text = baseCity + ' ' + (planText || '');
		if (text.indexOf('东京') !== -1) return ['新宿/银座/东京站', '浅草/上野/秋叶原', '池袋/品川'];
		if (text.indexOf('九江') !== -1 || text.indexOf('庐山') !== -1) return ['九江市中心/火车站', '庐山牯岭镇', '八里湖/浔阳区'];
		if (text.indexOf('上海') !== -1) return ['人民广场/南京路', '陆家嘴/外滩', '徐家汇/静安'];
		if (text.indexOf('北京') !== -1) return ['王府井/天安门', '前门/什刹海', '国贸/三里屯'];
		return [baseCity + '市中心', baseCity + '景区附近', baseCity + '交通枢纽周边'];
	}

	function renderHotelCard(hotel) {
		return [
			'<article class="hotel-card">',
			'<div class="hotel-card-head"><div><h4>' + escapeHtml(hotel.name) + '</h4><p><i class="fa fa-map-marker"></i> ' + escapeHtml(hotel.area) + '</p></div><strong>约 ' + hotel.price + ' 元/晚</strong></div>',
			'<div class="hotel-tags">' + hotel.tags.map(function (tag) { return '<span>' + escapeHtml(tag) + '</span>'; }).join('') + '</div>',
			'<p class="hotel-reason">' + escapeHtml(hotel.reason) + '</p>',
			'<div class="hotel-actions"><button type="button" class="save-hotel-btn">加入行程</button></div>',
			'</article>'
		].join('');
	}

	function addChat(role, text) {
		var node = document.createElement('div');
		node.className = 'chat-bubble ' + role;
		node.textContent = text;
		chatLog.appendChild(node);
		chatLog.scrollTop = chatLog.scrollHeight;
	}

	function buildSummary(values) {
		var items = [];
		if (values.country) items.push(['目的地', values.country]);
		if (values.city) items.push(['城市', values.city]);
		if (values.check_in) items.push(['出发', values.check_in]);
		if (values.check_out) items.push(['返回', values.check_out]);
		if (values.days) items.push(['天数', values.days + '天']);
		if (values.people) items.push(['人数', values.people + '人']);
		if (values.budget) items.push(['预算', values.budget]);
		return items.map(function (item) {
			return '<span><b>' + escapeHtml(item[0]) + '</b>' + escapeHtml(item[1]) + '</span>';
		}).join('');
	}

	function renderRoute(text, tab) {
		var source = tab && tab !== 'overview' ? getDayText(text, tab) : text;
		var html = escapeHtml(source);
		html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a class="spot-link" href="$2" target="_blank" rel="noopener">$1</a>');
		html = html.replace(/^###\s*(.+)$/gm, '<h4>$1</h4>');
		html = html.replace(/^##\s*(.+)$/gm, '<h3>$1</h3>');
		html = html.replace(/^#\s*(.+)$/gm, '<h3>$1</h3>');
		html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
		html = html.replace(/^\s*(第\d+天.*?)$/gm, '<h3>$1</h3>');
		html = html.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
		html = html.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<li><em>$1.</em> $2</li>');
		html = html.replace(/(<li>.*?<\/li>\n?)+/gs, function (block) { return '<ul>' + block + '</ul>'; });
		html = html.replace(/\n{2,}/g, '</p><p>');
		html = html.replace(/\n/g, '<br>');
		return '<p>' + html + '</p>';
	}

	function extractDaySections(text) {
		var sections = [];
		var regex = /(第\s*\d+\s*天[^\\n]*)/g;
		var seen = {};
		var match;
		while ((match = regex.exec(text)) !== null) {
			var title = match[1].replace(/\s+/g, '');
			var num = title.match(/\d+/);
			if (!num) continue;
			var key = 'day-' + num[0];
			if (seen[key]) continue;
			seen[key] = true;
			sections.push({ key: key, title: '第' + num[0] + '天' });
		}
		return sections;
	}

	function getDayText(text, key) {
		var dayNum = key.replace('day-', '');
		var regex = new RegExp('(第\\s*' + dayNum + '\\s*天[\\s\\S]*?)(?=\\n\\s*第\\s*\\d+\\s*天|$)');
		var match = text.match(regex);
		return match ? match[1] : text;
	}

	function escapeHtml(value) {
		return String(value || '')
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#039;');
	}
})();
