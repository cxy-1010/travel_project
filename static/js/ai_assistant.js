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

	var destination = trip.city || trip.country || '旅行目的地';
	var displayTitle = destination;
	if (trip.country && trip.city && trip.country !== trip.city) {
		displayTitle = trip.country + ' · ' + trip.city;
	}

	var statusEl = document.getElementById('assistant-status');
	var subtitleEl = document.getElementById('planner-subtitle');
	var reasoningEl = document.getElementById('ai-reasoning');
	var reasoningContent = document.getElementById('ai-reasoning-content');
	var responseEl = document.getElementById('ai-response');
	var responseContent = document.getElementById('ai-response-content');
	var errorEl = document.getElementById('ai-error');
	var errorContent = document.getElementById('ai-error-content');
	var thinkingDots = document.querySelector('.thinking-dots');

	setupDestination();
	startPlanning();

	function setupDestination() {
		document.getElementById('destination-title').textContent = displayTitle;
		document.getElementById('trip-summary').innerHTML = buildSummary(trip);

		var query = destination === '旅行目的地' ? 'travel landscape' : destination + ' 旅游';
		var imageUrl = getImageUrl(destination);
		var mapUrl = 'https://www.google.com/maps?q=' + encodeURIComponent(destination) + '&output=embed';
		var introUrl = 'https://zh.wikipedia.org/wiki/Special:Search?search=' + encodeURIComponent(destination);

		document.getElementById('destination-img').src = imageUrl;
		document.getElementById('destination-img').alt = displayTitle + '旅游图片';
		document.getElementById('destination-map').src = mapUrl;
		document.getElementById('intro-link').href = introUrl;
		document.getElementById('intro-link').textContent = '查看' + displayTitle + '介绍';
	}

	function getImageUrl(place) {
		var lower = (place || '').toLowerCase();
		var map = [
			{ keys: ['东京', 'tokyo', '日本', 'japan'], url: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['巴黎', 'paris', '法国', 'france'], url: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['伦敦', 'london', '英国', 'uk'], url: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['纽约', 'new york', '美国', 'usa'], url: 'https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['九江', '庐山', '江西'], url: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['上海'], url: 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?auto=format&fit=crop&w=1200&q=80' },
			{ keys: ['北京'], url: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=1200&q=80' }
		];

		for (var i = 0; i < map.length; i++) {
			for (var j = 0; j < map[i].keys.length; j++) {
				if (place.indexOf(map[i].keys[j]) !== -1 || lower.indexOf(map[i].keys[j]) !== -1) {
					return map[i].url;
				}
			}
		}
		return 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80';
	}

	function startPlanning() {
		fetch('/api/search/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(trip)
		}).then(function (response) {
			if (!response.ok) {
				return response.text().then(function (body) {
					throw new Error('服务器错误 (' + response.status + '): ' + body);
				});
			}

			var reader = response.body.getReader();
			var decoder = new TextDecoder();
			var buffer = '';
			var responseText = '';

			function processStream() {
				reader.read().then(function (result) {
					if (result.done) {
						return;
					}

					buffer += decoder.decode(result.value, { stream: true });
					var lines = buffer.split('\n');
					buffer = lines.pop();

					lines.forEach(function (rawLine) {
						var line = rawLine.trim();
						if (!line.startsWith('data: ')) return;

						try {
							var data = JSON.parse(line.substring(6));
							if (data.type === 'start') {
								statusEl.textContent = '正在拆解您的出行需求';
								subtitleEl.textContent = '路线、住宿、交通和预算正在同步规划';
							} else if (data.type === 'reasoning') {
								reasoningEl.style.display = 'block';
								reasoningContent.appendChild(document.createTextNode(data.content));
								reasoningContent.scrollTop = reasoningContent.scrollHeight;
							} else if (data.type === 'content') {
								responseEl.style.display = 'block';
								responseText += data.content;
								responseContent.innerHTML = renderTravelMarkdown(responseText);
								responseContent.scrollTop = responseContent.scrollHeight;
								statusEl.textContent = '正在生成定制行程';
							} else if (data.type === 'done') {
								statusEl.textContent = 'AI 已回答完成';
								subtitleEl.textContent = '方案已生成，可继续查看地图和目的地介绍';
								if (thinkingDots) thinkingDots.style.display = 'none';
							} else if (data.type === 'error') {
								showError(data.content);
							}
						} catch (err) {
							// Ignore incomplete JSON lines.
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

	function showError(message) {
		errorEl.style.display = 'block';
		errorContent.textContent = message;
		statusEl.textContent = '生成失败';
		subtitleEl.textContent = '请检查网络或稍后重试';
		if (thinkingDots) thinkingDots.style.display = 'none';
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
		if (!items.length) return '<span><b>需求</b>从首页搜索进入后自动生成</span>';
		return items.map(function (item) {
			return '<span><b>' + escapeHtml(item[0]) + '</b>' + escapeHtml(item[1]) + '</span>';
		}).join('');
	}

	function renderTravelMarkdown(text) {
		var escaped = escapeHtml(text);
		escaped = escaped.replace(/^###\s*(.+)$/gm, '<h4>$1</h4>');
		escaped = escaped.replace(/^##\s*(.+)$/gm, '<h3>$1</h3>');
		escaped = escaped.replace(/^#\s*(.+)$/gm, '<h3>$1</h3>');
		escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
		escaped = escaped.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
		escaped = escaped.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<li><em>$1.</em> $2</li>');
		escaped = escaped.replace(/(<li>.*?<\/li>\n?)+/gs, function (block) {
			return '<ul>' + block + '</ul>';
		});
		escaped = escaped.replace(/\n{2,}/g, '</p><p>');
		escaped = escaped.replace(/\n/g, '<br>');
		return '<p>' + escaped + '</p>';
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
