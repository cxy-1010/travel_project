(function () {
	'use strict';

	var params = new URLSearchParams(window.location.search);
	var state = {
		country: params.get('country') || '',
		city: params.get('city') || '上海',
		checkIn: params.get('check_in') || '',
		checkOut: params.get('check_out') || '',
		rooms: params.get('rooms') || '1',
		guests: params.get('guests') || '1',
		keyword: params.get('keyword') || '',
		sort: 'value',
		priceFilter: ''
	};
	var hotels = [];
	var hasSearched = false;

	var cityInput = document.getElementById('hotel-city');
	var checkinInput = document.getElementById('hotel-checkin');
	var checkoutInput = document.getElementById('hotel-checkout');
	var guestsInput = document.getElementById('hotel-guests');
	var keywordInput = document.getElementById('hotel-keyword');
	var resultTitle = document.getElementById('result-title');
	var hotelList = document.getElementById('hotel-list');
	var sortSelect = document.getElementById('sort-select');
	var priceFilters = document.getElementById('price-filters');
	var aiNote = document.getElementById('ai-hotel-note');
	var aiFindBtn = document.getElementById('ai-find-hotels-btn');
	var hotelSearchBtn = document.getElementById('hotel-search-btn');
	var hotelMap = document.getElementById('hotel-map');
	var showMapBtn = document.getElementById('show-map-btn');
	var loadingTimer = null;
	var loadingStartedAt = 0;
	var loadingStepIndex = 0;
	var loadingSteps = [
		{
			title: '正在连接 AI 酒店搜索',
			detail: '已收到目的地和入住信息，正在准备请求。',
			hint: '首次连接模型或网络代理较慢时，这一步会多等几秒。'
		},
		{
			title: '正在筛选酒店候选',
			detail: 'AI 正在按城市、位置、价格和评分整理酒店。',
			hint: '页面没有卡住，搜索完成后会一次性显示酒店列表。'
		},
		{
			title: '正在补全详情网址',
			detail: '正在为每家酒店生成可打开的详情或搜索链接。',
			hint: '酒店搜索需要返回结构化 JSON，所以比普通聊天更慢一些。'
		},
		{
			title: '正在校验结果',
			detail: '正在避免把其他城市的酒店混进当前目的地。',
			hint: '请稍等，不需要重复点击搜索按钮。'
		}
	];

	init();

	function init() {
		cityInput.value = state.city;
		checkinInput.value = state.checkIn;
		checkoutInput.value = state.checkOut;
		guestsInput.value = state.rooms + '间, ' + state.guests + '成人';
		keywordInput.value = state.keyword;
		updateMap();
		hotels = [];
		render();
	}

	hotelSearchBtn.addEventListener('click', function () {
		searchHotelsWithAi();
	});

	aiFindBtn.addEventListener('click', function () {
		searchHotelsWithAi();
	});

	showMapBtn.addEventListener('click', function () {
		state.city = cityInput.value.trim() || '上海';
		window.open('https://www.google.com/maps/search/' + encodeURIComponent(state.city + ' 酒店'), '_blank', 'noopener');
	});

	function searchHotelsWithAi() {
		state.city = cityInput.value.trim() || '上海';
		state.checkIn = checkinInput.value.trim();
		state.checkOut = checkoutInput.value.trim();
		state.keyword = keywordInput.value.trim();
		updateMap();
		hasSearched = true;
		hotels = [];
		setSearching(true);

		fetch('/api/hotel-search/', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				city: state.city,
				check_in: state.checkIn,
				check_out: state.checkOut,
				guests: guestsInput.value,
				keyword: state.keyword
			})
		}).then(function (response) {
			if (!response.ok) {
				throw new Error('AI 查找失败：服务器返回 ' + response.status);
			}
			return readHotelStream(response);
		}).catch(function (err) {
			hotels = [];
			aiNote.innerHTML = '<i class="fa fa-warning"></i> AI 查找失败：' + escapeHtml(err.message) + '。请检查网络或 DeepSeek 配置后重试。';
			render();
		}).finally(function () {
			setSearching(false);
		});
	}

	function readHotelStream(response) {
		var reader = response.body.getReader();
		var decoder = new TextDecoder();
		var buffer = '';
		var received = 0;

		function pump() {
			return reader.read().then(function (result) {
				if (result.done) {
					if (!received) throw new Error('AI 没有返回可用酒店');
					return;
				}

				buffer += decoder.decode(result.value, { stream: true });
				var events = buffer.split('\n\n');
				buffer = events.pop();
				var streamError = null;

				events.forEach(function (eventText) {
					if (streamError) return;
					var line = eventText.split('\n').find(function (item) {
						return item.indexOf('data: ') === 0;
					});
					if (!line) return;
					try {
						var data = JSON.parse(line.substring(6));
						if (data.type === 'start') {
							updateLoadingStep({
								title: data.cached ? '正在读取缓存结果' : '正在连接 AI 酒店搜索',
								detail: data.cached ? '相同条件刚刚查过，正在快速显示结果。' : '连接成功后会逐个显示酒店。',
								hint: '第一家酒店出来后会立即显示在列表里。'
							});
						} else if (data.type === 'status') {
							updateLoadingStep({
								title: '正在逐个生成酒店',
								detail: data.content || 'AI 正在返回酒店。',
								hint: '不需要等全部完成，酒店卡片会陆续出现。'
							});
						} else if (data.type === 'hotel') {
							appendStreamHotel(data.hotel);
							received += 1;
							stopLoadingProgress();
							aiNote.innerHTML = '<i class="fa fa-spinner fa-spin"></i> 已找到 ' + received + ' 家，AI 还在继续补充...';
							aiNote.classList.remove('loading');
						} else if (data.type === 'done') {
							if (!received && !hotels.length) throw new Error('AI 没有返回可用酒店');
							aiNote.innerHTML = '<i class="fa fa-check"></i> AI 已找到 ' + hotels.length + ' 家酒店，“查看详情”已绑定 AI 返回的网址。';
						} else if (data.type === 'error') {
							streamError = new Error(data.content || 'AI 查找失败');
						}
					} catch (err) {
						streamError = err;
					}
				});
				if (streamError) throw streamError;

				return pump();
			});
		}

		return pump();
	}

	function appendStreamHotel(item) {
		var normalized = normalizeAiHotels([item])[0];
		if (!normalized) return;
		var exists = hotels.some(function (hotel) {
			return hotel.name === normalized.name;
		});
		if (exists) return;
		hotels.push(normalized);
		render();
	}

	function setSearching(isSearching) {
		aiFindBtn.disabled = isSearching;
		hotelSearchBtn.disabled = isSearching;
		aiFindBtn.innerHTML = isSearching ? '<i class="fa fa-spinner fa-spin"></i> 查找中' : '<i class="fa fa-bolt"></i> AI查找酒店';
		hotelSearchBtn.innerHTML = isSearching ? '<i class="fa fa-spinner fa-spin"></i> 搜索中' : '<i class="fa fa-search"></i> 搜索';
		if (isSearching) {
			startLoadingProgress();
			return;
		}
		stopLoadingProgress();
	}

	function startLoadingProgress() {
		stopLoadingProgress();
		loadingStartedAt = Date.now();
		loadingStepIndex = 0;
		updateLoadingStep(loadingSteps[0]);
		renderHotelLoadingCards();
		loadingTimer = window.setInterval(function () {
			var elapsed = Math.floor((Date.now() - loadingStartedAt) / 1000);
			var nextIndex = Math.min(Math.floor(elapsed / 5), loadingSteps.length - 1);
			if (nextIndex !== loadingStepIndex) {
				loadingStepIndex = nextIndex;
				updateLoadingStep(loadingSteps[loadingStepIndex]);
			} else {
				updateLoadingStep(loadingSteps[loadingStepIndex]);
			}
		}, 1000);
	}

	function stopLoadingProgress() {
		if (loadingTimer) {
			window.clearInterval(loadingTimer);
			loadingTimer = null;
		}
		aiNote.classList.remove('loading');
	}

	function updateLoadingStep(step) {
		var elapsed = Math.floor((Date.now() - loadingStartedAt) / 1000);
		var progress = Math.min(18 + elapsed * 4, 92);
		aiNote.classList.add('loading');
		aiNote.innerHTML = [
			'<div class="hotel-loading-note-head">',
			'<span class="hotel-loading-pulse"></span>',
			'<div><strong>' + escapeHtml(step.title) + '</strong><p>' + escapeHtml(step.detail) + '</p></div>',
			'<span class="hotel-loading-seconds">' + elapsed + '秒</span>',
			'</div>',
			'<div class="hotel-loading-progress"><span style="width:' + progress + '%"></span></div>',
			'<div class="hotel-loading-hint">' + escapeHtml(step.hint) + '</div>'
		].join('');
	}

	function renderHotelLoadingCards() {
		resultTitle.textContent = '正在查找' + state.city + '酒店';
		hotelList.innerHTML = [0, 1, 2].map(function () {
			return [
				'<article class="hotel-card hotel-card-loading">',
				'<div class="hotel-img loading-block"></div>',
				'<div class="hotel-info">',
				'<div class="hotel-main">',
				'<div class="loading-line title"></div>',
				'<div class="loading-line short"></div>',
				'<div class="loading-line medium"></div>',
				'<div class="room-box loading-room">',
				'<div class="loading-line"></div>',
				'<div class="loading-line short"></div>',
				'<div class="loading-tags"><span></span><span></span><span></span></div>',
				'</div>',
				'</div>',
				'<div class="hotel-side">',
				'<div class="loading-line score"></div>',
				'<div class="loading-line price"></div>',
				'<div class="loading-button"></div>',
				'</div>',
				'</div>',
				'</article>'
			].join('');
		}).join('');
	}

	sortSelect.addEventListener('change', function () {
		state.sort = sortSelect.value;
		render();
	});

	priceFilters.addEventListener('click', function (event) {
		var button = event.target.closest('button');
		if (!button) return;
		state.priceFilter = state.priceFilter === button.dataset.price ? '' : button.dataset.price;
		Array.prototype.forEach.call(priceFilters.querySelectorAll('button'), function (btn) {
			btn.classList.toggle('active', btn.dataset.price === state.priceFilter);
		});
		render();
	});

	function render() {
		var list = applyFilters(hotels);
		resultTitle.textContent = hasSearched ? '找到' + list.length + '家' + state.city + '酒店' : state.city + '酒店智能搜索';
		if (!hasSearched) {
			hotelList.innerHTML = '<div class="empty-state"><i class="fa fa-magic"></i><strong>点击“AI查找酒店”开始搜索</strong><span>查找完成后会在这里显示 10-20 家酒店，并自动绑定详情网址。</span></div>';
			return;
		}
		if (!list.length) {
			hotelList.innerHTML = '<div class="empty-state"><i class="fa fa-search"></i><strong>暂时没有可显示的酒店</strong><span>可以更换城市、关键词或价格筛选后重新点击 AI 查找。</span></div>';
			return;
		}
		hotelList.innerHTML = list.map(renderHotel).join('');
	}

	function applyFilters(source) {
		var list = source.slice();
		if (state.priceFilter) {
			var parts = state.priceFilter.split('-').map(Number);
			list = list.filter(function (hotel) {
				return hotel.price >= parts[0] && hotel.price <= parts[1];
			});
		}
		if (state.keyword) {
			list = list.filter(function (hotel) {
				return hotel.name.indexOf(state.keyword) !== -1 || hotel.area.indexOf(state.keyword) !== -1;
			});
		}
		list.sort(function (a, b) {
			if (state.sort === 'priceAsc') return a.price - b.price;
			if (state.sort === 'priceDesc') return b.price - a.price;
			if (state.sort === 'rating') return b.rating - a.rating;
			return b.valueScore - a.valueScore;
		});
		return list;
	}

	function renderHotel(hotel) {
		return [
			'<article class="hotel-card">',
			'<img class="hotel-img" src="' + hotel.image + '" alt="' + escapeHtml(hotel.name) + '">',
			'<div class="hotel-info">',
			'<div class="hotel-main">',
			'<h2>' + escapeHtml(hotel.name) + ' <span class="stars">★★★★★</span></h2>',
			'<div class="rating-line"><span class="score">' + hotel.rating + '</span><strong>' + ratingText(hotel.rating) + '</strong><span>' + hotel.reviewCount.toLocaleString() + '条点评</span><span class="comment">“位置方便，服务细致”</span></div>',
			'<div class="location"><i class="fa fa-map-marker"></i> ' + escapeHtml(hotel.area) + ' · 查看地图</div>',
			'<div class="room-box"><strong>' + escapeHtml(hotel.room) + ' 👤👤 🛏</strong><span>免费取消 · 近期预订热度较高</span><div class="tags">' + hotel.tags.map(function (tag) { return '<span>' + escapeHtml(tag) + '</span>'; }).join('') + '</div></div>',
			'</div>',
			'<div class="hotel-side"><div class="value-score">性价比 ' + hotel.valueScore + '</div><div class="price">¥' + hotel.price + '<small> 起</small></div><a class="detail-btn" href="' + escapeHtml(hotel.detailUrl) + '" target="_blank" rel="noopener">查看详情</a></div>',
			'</div>',
			'</article>'
		].join('');
	}

	function getAreas(city) {
		if (city.indexOf('上海') !== -1) return ['人民广场/南京路', '外滩/陆家嘴', '虹桥枢纽', '徐家汇/静安寺', '迪士尼度假区'];
		if (city.indexOf('北京') !== -1) return ['王府井/天安门', '前门/什刹海', '国贸/三里屯', '西单/金融街', '北京南站'];
		if (city.indexOf('九江') !== -1 || city.indexOf('庐山') !== -1) return ['九江站/市中心', '浔阳区', '八里湖新区', '庐山牯岭镇', '濂溪区'];
		if (city.indexOf('东京') !== -1) return ['新宿', '银座/东京站', '浅草/上野', '涩谷', '池袋'];
		return [city + '市中心', city + '景区附近', city + '火车站', city + '商圈', city + '度假区'];
	}

	function getImages(city) {
		if (city.indexOf('上海') !== -1) {
			return [
				'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80',
				'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=900&q=80',
				'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=900&q=80',
				'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?auto=format&fit=crop&w=900&q=80'
			];
		}
		return [
			'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80',
			'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=900&q=80',
			'https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=900&q=80',
			'https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=900&q=80'
		];
	}

	function normalizeAiHotels(items) {
		if (!Array.isArray(items)) return [];
		return items.slice(0, 20).map(function (item, index) {
			var name = cleanCityPlaceholder(item.name || (state.city + '精选酒店'));
			var area = cleanCityPlaceholder(item.area || state.city + '市中心');
			var price = Number(item.price) || (360 + index * 80);
			var rating = Number(item.rating) || 4.5;
			var detailUrl = normalizeUrl(item.detailUrl, state.city, name);
			var valueScore = Number((rating * 20 - price / 80 + 25).toFixed(1));
			return {
				name: name,
				area: area,
				room: item.room || '高级大床房',
				price: price,
				rating: rating,
				reviewCount: Number(item.reviewCount) || (1200 + index * 357),
				valueScore: valueScore,
				image: imageFromQuery(item.imageQuery || name),
				detailUrl: detailUrl,
				tags: Array.isArray(item.tags) ? item.tags.slice(0, 3) : ['AI推荐', '可比价']
			};
		});
	}

	function imageFromQuery(query) {
		var lower = String(query || '').toLowerCase();
		if (lower.indexOf('luxury') !== -1 || query.indexOf('豪华') !== -1) {
			return 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=900&q=80';
		}
		if (query.indexOf('温泉') !== -1 || query.indexOf('度假') !== -1) {
			return 'https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=900&q=80';
		}
		if (query.indexOf('城市') !== -1 || query.indexOf('中心') !== -1) {
			return 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=900&q=80';
		}
		return getImages(state.city)[Math.floor(pseudoRandom(query) * getImages(state.city).length)];
	}

	function buildDetailUrl(city, hotelName) {
		return 'https://www.bing.com/search?q=' + encodeURIComponent(city + ' ' + hotelName + ' 酒店 官网');
	}

	function normalizeUrl(url, city, hotelName) {
		var value = String(url || '').trim();
		if (/^https?:\/\//i.test(value) && value.indexOf('??') === -1 && value.indexOf('%3F') === -1 && value.indexOf('%3f') === -1) return value;
		return buildDetailUrl(city, hotelName);
	}

	function cleanCityPlaceholder(value) {
		return String(value || '')
			.replace(/\?\?/g, state.city)
			.replace(/某城市/g, state.city)
			.replace(/目标城市/g, state.city);
	}

	function updateMap() {
		hotelMap.src = 'https://www.google.com/maps?q=' + encodeURIComponent((cityInput.value.trim() || state.city) + ' 酒店') + '&output=embed';
	}

	function ratingText(score) {
		if (score >= 4.8) return '超棒';
		if (score >= 4.6) return '很好';
		return '不错';
	}

	function pseudoRandom(seed) {
		var str = String(seed);
		var h = 0;
		for (var i = 0; i < str.length; i++) h = Math.imul(31, h) + str.charCodeAt(i) | 0;
		return Math.abs(Math.sin(h) * 10000) % 1;
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
