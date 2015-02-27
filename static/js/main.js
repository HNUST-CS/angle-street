(function() {
  var QINIU_BUCKET, adminNavCtrl, adminlogCtrl, adminotherCtrl, editshopCtrl, listOrderCtrl, loginCtrl, mainCtrl, orderCtrl, orderService, qiniuimg, shopCtrl, shopListCtrl, stringtojson, userCtrl;

  window.indexApp = angular.module("index", ["ngRoute", "ngCookies"]);

  indexApp.config(function($routeProvider, $locationProvider) {
    return $routeProvider.when("/", {
      redirectTo: "/menu"
    }).when("/menu", {
      templateUrl: "/static/template/menu.html"
    }).when("/shop", {
      templateUrl: "/static/template/shoplist.html"
    }).when("/order/:id", {
      templateUrl: "/static/template/order.html"
    }).when("/shop/:id", {
      templateUrl: "/static/template/shop.html"
    }).when("/shop/:id/shopdetail", {
      templateUrl: "/static/template/shopdetail.html"
    }).otherwise({
      redirectTo: "/"
    });
  });

  shopListCtrl = function($scope, $http) {
    window.w = $scope;
    $http.get("/api/listshop", {
      cache: true
    }).success(function(data) {
      return $scope.shopList = data;
    });
  };

  shopCtrl = function($scope, $http, $routeParams, orderService, $location) {
    var recalcuteOrder;
    window.w = $scope;
    $scope.order = orderService.readOrder();
    $scope.id = $routeParams.id;
    recalcuteOrder = function() {
      var T, _ref;
      T = $scope.order;
      _.each(T.goods, function(k, v) {
        if (k === 0) {
          return delete T.goods[v];
        }
      });
      _ref = _(T.goods).chain().pairs().reduce(function(s, n) {
        return [s[0] + n[1], s[1] + $scope.shopData.priceList[n[0]] * n[1]];
      }, [0, 0]).value(), T.allcount = _ref[0], T.allprice = _ref[1];
      return orderService.setOrder($scope.order);
    };
    $http.get("/api/shop/" + $scope.id).success(function(data) {
      var i, _i, _len, _ref;
      $scope.shopData = data;
      $scope.category = _($scope.shopData.goods).chain().filter(function(s) {
        return s.show;
      }).pluck("category").groupBy().map(function(n) {
        return {
          "name": n[0],
          "count": n.length
        };
      }).sortBy(function(n) {
        return -n.count;
      }).value();
      $scope.shopData.priceList = {};
      _ref = $scope.shopData.goods;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        i = _ref[_i];
        $scope.shopData.priceList[i.id] = parseInt(i.price);
      }
      return $scope.changeCategory("热卖");
    });
    $scope.changeCategory = function(name) {
      var T;
      $scope.categoryNow = name;
      T = _($scope.shopData.goods).chain();
      if (name === "热卖") {
        $scope.goods = T.sortBy(function(n) {
          return -n.salesVolume;
        }).first(5).value();
      } else if (name === "我的订单") {
        $scope.goods = T.filter(function(n) {
          return $scope.order.goods[n.id] > 0;
        }).sortBy(function(n) {
          return -n.salesVolume;
        }).value();
      } else {
        $scope.goods = T.filter(function(n) {
          return ~n.category.indexOf($scope.categoryNow);
        }).sortBy(function(n) {
          return -n.salesVolume;
        }).value();
      }
      return recalcuteOrder();
    };
    $scope.clickAdd = function(id, value) {
      if ($scope.order.goods[id] == null) {
        $scope.order.goods[id] = 0;
      }
      $scope.order.goods[id] += value;
      if ($scope.order.goods[id] < 0) {
        $scope.order.goods[id] = 0;
      }
      return recalcuteOrder();
    };
    $scope.clickOrder = function() {
      orderService.setOrder($scope.order);
      if ($scope.categoryNow !== "我的订单") {
        $scope.categoryNow = "我的订单";
        $scope.changeCategory("我的订单");
        return;
      }
      return $location.path("/order/" + $routeParams.id);
    };
    $scope.showModal = function(img, name, price, salesVolume) {
      if (img) {
        $scope.itemModal = {
          img: img,
          name: name,
          price: price,
          salesVolume: salesVolume
        };
        return $('#item_pic_m').modal('show');
      }
    };
  };

  orderCtrl = function($scope, $http, $routeParams, $location, orderService) {
    $scope.order = orderService.readOrder();
    $scope.clickReturn = function() {
      orderService.setOrder($scope.order);
      return $location.path("/#/shop/" + $routeParams.id);
    };
    $scope.clickOrderSubmit = function() {
      var order;
      orderService.setOrder($scope.order);
      order = orderService.readOrder();
      $scope.disable = true;
      $http.post('/api/submitorder', order).success(function(data) {
        $scope.msg = data.msg;
        $scope.disable = false;
        if (!data.error) {
          orderService.reset();
          return $scope.order = orderService.readOrder();
        }
      });
      return console.log(order);
    };
    $scope.saveContent = function() {
      return orderService.setOrder($scope.order);
    };
  };

  orderService = function($http, $cookieStore, $routeParams) {
    var init, _order, _ref;
    _order = (_ref = $cookieStore.get("order")) != null ? _ref : {};
    (init = function() {
      return _.defaults(_order, {
        "goods": {},
        "allcount": 0,
        "allprice": 0,
        "name": "",
        "tel": "",
        "addr": "",
        "msg": "",
        "shopId": $routeParams.id
      });
    })();
    this.reset = function() {
      _order = _.omit(_order, ['shopId', 'goods', 'allprice', 'allcount']);
      init();
      return $cookieStore.put("order", _order);
    };
    this.setOrder = function(order) {
      _order = order;
      return $cookieStore.put("order", _order);
    };
    this.readOrder = function() {
      if ($routeParams.id !== _order.shopId) {
        _order = _.omit(_order, ['shopId', 'goods', 'allprice', 'allcount']);
        init();
        $cookieStore.put("order", _order);
      }
      return _order;
    };
    this.addInf = function(name, tel, addr) {
      _order.name = name;
      _order.tel = tel;
      _order.addr = addr;
      return $cookieStore.put("order", _order);
    };
  };

  indexApp.controller("shopCtrl", shopCtrl);

  indexApp.controller("shopListCtrl", shopListCtrl);

  indexApp.service("orderService", orderService);

  indexApp.controller("orderCtrl", orderCtrl);

  window.adminApp = angular.module("admin", ["ngAnimate", "ngRoute", "ngCookies", "ngToast"]);

  adminApp.config(function($routeProvider, $locationProvider) {
    $routeProvider.when("/admin", {
      templateUrl: "/static/admintemplate/adminmain.html"
    }).when("/admin/login", {
      templateUrl: "/static/admintemplate/adminlogin.html"
    }).when("/admin/listuser", {
      templateUrl: "/static/admintemplate/adminlistuser.html"
    }).when("/admin/listshop", {
      templateUrl: "/static/admintemplate/adminlistshop.html"
    }).when("/admin/listorder", {
      templateUrl: "/static/admintemplate/adminlistorder.html"
    }).when("/admin/editshop/:id", {
      templateUrl: "/static/admintemplate/admineditshop.html"
    }).when("/admin/log", {
      templateUrl: "/static/admintemplate/adminlog.html"
    }).when("/admin/other", {
      templateUrl: "/static/admintemplate/adminother.html"
    }).otherwise({
      redirectTo: "/admin"
    });
    return $locationProvider.html5Mode(true);
  });

  

adminApp.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

adminApp.service('fileUpload', ['$http', function ($http) {
    this.uploadFileToUrl = function(file, uploadUrl,cb){
        var fd = new FormData();
        fd.append('file', file);  
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        })
        .success(function(data){
          cb(data);
        })
        .error(function(){
        });
    }
}]);

;

  mainCtrl = function($scope, $http, $interval, $location, ngToast) {
    if ($scope.login.isLogin === false) {
      $location.path("/admin/login");
      ngToast.create('你没有登陆或者已经登陆超时,请成功登陆');
    }
    return $scope.logout = function() {
      return $http.get('/api/logout').success(function(data) {
        if (data.error === false) {
          $scope.updateLoginState();
          $location.path("/admin/login");
          return ngToast.create('退出登陆成功');
        }
      });
    };
  };

  adminNavCtrl = function($scope, $http, $interval, $location, ngToast) {
    $scope.login = {};
    $scope.updateLoginState = function(showmsg) {
      if (showmsg == null) {
        showmsg = false;
      }
      return $http.get('/api/islogin').success(function(data) {
        if (data.error) {
          $location.path("/admin/login");
          $scope.login.isLogin = false;
          if (showmsg) {
            return ngToast.create('你还没有登陆');
          }
        } else {
          $scope.username = data.username;
          $scope.login.isLogin = true;
          if (showmsg) {
            ngToast.create('欢迎登陆,' + data.username);
          }
          if ($location.url() === '/admin/login') {
            return $location.path("/admin");
          }
        }
      });
    };
    $interval($scope.updateLoginState(false), 1000 * 60);
    return $scope.updateLoginState();
  };

  loginCtrl = function($scope, $http, $interval, $location, ngToast) {
    $scope.username = "";
    $scope.passwd = "";
    return $scope.login = function() {
      var p;
      p = {
        username: $scope.username,
        passwd: $scope.passwd
      };
      return $http.post('/api/login', p).success(function(data) {
        console.log(data);
        if (data.error) {
          return ngToast.create({
            content: data.msg,
            "class": "danger"
          });
        } else {
          ngToast.create('登陆成功');
          return $scope.updateLoginState(false);
        }
      });
    };
  };

  userCtrl = function($scope, $http, $interval, $location, ngToast) {
    var init;
    $scope.updateLoginState(false);
    $scope.msg = "";
    $scope.state = "add";
    ($scope.clear = function() {
      return $scope.usernow = {
        username: "",
        passwd: "",
        comment: "",
        role: "",
        tel: "",
        qq: ""
      };
    })();
    $scope.clear();
    (init = function() {
      return $http.get('/api/admin/listuser').success(function(data) {
        if (data.error) {
          if (data.msg === "没有权限") {
            $scope.updateLoginState(true);
          }
          return;
        }
        return $scope.users = data;
      });
    })();
    $scope.choose = function(user) {
      $scope.usernow = _.clone(user);
      return $scope.state = 'edit';
    };
    $scope.add = function() {
      if ($scope.state === 'add') {
        return $http.post('/api/admin/adduser', $scope.usernow).success(function(data) {
          $scope.msg = data.msg;
          ngToast.create(data.msg);
          return init();
        });
      } else {
        $scope.clear();
        return $scope.state = 'add';
      }
    };
    $scope.update = function() {
      $http.post('/api/admin/updateuser', $scope.usernow).success(function(data) {
        $scope.msg = data.msg;
        return ngToast.create(data.msg);
      });
      return init();
    };
    return $scope.del = function() {
      return $http.post('/api/admin/deluser', $scope.usernow).success(function(data) {
        $scope.msg = data.msg;
        ngToast.create(data.msg);
        return init();
      });
    };
  };

  shopCtrl = function($scope, $http, $interval, $location, fileUpload, $timeout, ngToast) {
    var init;
    $scope.updateLoginState();
    window.w = $scope;
    $scope.state = "new";
    $scope.upload = function() {
      var file, uploadUrl;
      file = $scope.myFile;
      if (!file) {
        ngToast.create("没有选择文件");
        return;
      }
      uploadUrl = "/api/admin/upload";
      fileUpload.uploadFileToUrl(file, uploadUrl, function(data) {
        if (data.$error) {
          ngToast.create(data.msg);
        }
        ngToast.create("文件上传成功");
        return $scope.shopnow.info.shopImg = data.url;
      });
    };
    ($scope.clear = function() {
      return $scope.shopnow = {
        info: {
          name: "",
          tel: "",
          city: "",
          shopImg: "1",
          deliveryTime: "30",
          freePrice: "",
          area: "",
          addPrice: "10",
          state: "营业",
          startPrice: "12",
          msg: "",
          desc: "",
          shortName: "",
          addr: "湘潭市",
          weixin: ""
        },
        data: {
          show: true,
          admin: "",
          star: "5",
          proority: "0"
        },
        goods: [],
        shopImg: "1"
      };
    })();
    (init = function() {
      return $http.get('/api/admin/listshop').success(function(data) {
        console.log(data);
        if (data.error) {
          if (data.msg === "没有权限") {
            $scope.updateLoginState(true);
          }
          return;
        }
        return $scope.shops = data;
      });
    })();
    $scope.add = function() {
      if ($scope.state === "edit") {
        $scope.clear();
        $scope.state = "new";
        return;
      }
      if ($scope.state === "new") {
        console.log('add shop', $scope.shopnow);
        return $http.post('/api/admin/addshop', $scope.shopnow).success(function(data) {
          console.log(data);
          ngToast.create(data.msg);
          return init();
        });
      }
    };
    $scope.del = function() {
      return $http.post('/api/admin/delshop', $scope.shopnow).success(function(data) {
        console.log(data);
        return ngToast.create(data.msg);
      });
    };
    $scope.choose = function(shop) {
      $scope.state = "edit";
      $scope.shopnow = shop;
      return $scope.shopnow.id = shop._id.$oid;
    };
    $scope.update = function() {
      if ($scope.state === "new") {
        ngToast.create("选择店铺之后才能更新哦");
        return;
      }
      return $http.post('/api/admin/updateshop', $scope.shopnow).success(function(data) {
        console.log(data);
        $scope.shops = data;
        ngToast.create(data.msg);
        return init();
      });
    };
    return $scope.completionWeixin = function() {
      var w;
      w = $scope.shopnow.info.weixin;
      if (!w) {
        return;
      }
      return $http.get('/api/admin/filteropenid/' + w).success(function(data) {
        if (data.length > w.length) {
          return $scope.shopnow.info.weixin = data;
        }
      });
    };
  };

  editshopCtrl = function($scope, $http, $interval, $location, $routeParams, $timeout, fileUpload, ngToast) {
    var init;
    window.w = $scope;
    $scope.state = "new";
    ($scope.clear = function() {
      var _ref;
      $scope.good = {
        id: _.max(_((_ref = $scope.shop) != null ? _ref.goods : void 0).pluck('id')) + 1,
        name: "",
        category: "",
        img: "",
        show: true,
        price: 10.0,
        salesVolume: 0,
        point: 0,
        desc: ""
      };
      return $scope.now = 'add';
    })();
    $scope.upload = function() {
      var file, uploadUrl;
      file = $scope.myFile;
      console.log("file is " + JSON.stringify(file));
      uploadUrl = "/api/admin/upload";
      fileUpload.uploadFileToUrl(file, uploadUrl, function(data) {
        console.log(data);
        return $scope.good.img = data.url;
      });
    };
    $scope.add = function() {
      if ($scope.state === "edit") {
        $scope.clear();
        $scope.state = "new";
        return;
      }
      if ($scope.shopform.$valid) {
        console.log('add good', $scope.good);
        $scope.shop.goods.push($scope.good);
        $scope.clear();
        return ngToast.create("成功新增,你必须按保存键才能生效");
      } else {
        return ngToast.create("你的填写不完全,添加失败");
      }
    };
    $scope.choose = function(shop) {
      $scope.state = "edit";
      return $scope.good = shop;
    };
    $scope.del = function() {
      var good, index, _i, _len, _ref;
      if ($scope.state === "new") {
        return;
      }
      _ref = $scope.shop.goods;
      for (index = _i = 0, _len = _ref.length; _i < _len; index = ++_i) {
        good = _ref[index];
        if (good === $scope.good) {
          $scope.shop.goods.splice(index, 1);
          ngToast.create("成功删除,你必须按保存键才能生效");
          return;
        }
      }
    };
    $scope.save = function() {
      $scope.shop.id = $routeParams.id;
      return $http.post('/api/admin/updateshopgoods', $scope.shop).success(function(data) {
        console.log(data);
        ngToast.create(data.msg);
        return init();
      });
    };
    return (init = function() {
      console.log($scope.id = $routeParams.id);
      return $http.get('/api/admin/shopinfo/' + $scope.id).success(function(data) {
        if (data.error) {
          if (data.msg === "没有权限") {
            $scope.updateLoginState(true);
            return;
          }
          ngToast(data.msg);
        }
        console.log(data);
        $scope.shop = data;
        return $scope.clear();
      });
    })();
  };

  listOrderCtrl = function($scope, $http, $interval, $location, $routeParams, fileUpload, ngToast) {
    window.jQuery(function() {
      return $('.tips').tooltip('hide');
    });
    $scope.updateLoginState();
    window.w = $scope;
    $scope.state = "all";
    $scope.page = 0;
    $scope.chooseState = function(state) {
      $scope.state = state;
      $scope.page = 0;
      return $scope.reload();
    };
    $scope.lastpage = function() {
      if ($scope.page > 0) {
        $scope.page--;
        return $scope.reload();
      }
    };
    $scope.nextpage = function() {
      $scope.page++;
      return $scope.reload();
    };
    ($scope.reload = function() {
      return $http.get('/api/admin/listorder/' + $scope.state + '/' + $scope.page).success(function(data) {
        if (data.length === 0 && $scope.page > 0) {
          ngToast.create("没有这一页了。");
          $scope.page--;
          return;
        }
        $scope.orderlist = data;
        return $scope.orderNow = $scope.orderlist[0];
      });
    })();
    $scope.choose = function(item) {
      return $scope.orderNow = item;
    };
    $scope.sendCmd = function(cmd) {
      var data;
      data = {
        cmd: cmd,
        id: $scope.orderNow._id.$oid
      };
      return $http.post('/api/admin/ordercmd', data).success(function(data) {
        if (data.error) {
          ngToast.create({
            "class": "error"
          }, data.msg);
        } else {
          ngToast.create(data.msg);
        }
        return $scope.reload();
      });
    };
    return $scope.orderModifyState = function(state) {
      var data;
      data = {
        state: state,
        id: $scope.orderNow._id.$oid
      };
      return $http.post('/api/admin/ordermodifystate', data).success(function(data) {
        ngToast.create(data.msg);
        return $scope.reload();
      });
    };
  };

  adminlogCtrl = function($scope, $http) {
    var un;
    un = function(s) {
      return unescape(s.replace(/\\/g, "%"));
    };
    return $http.get('/api/admin/log/0').success(function(data) {
      return $scope.log = _(data).map(function(it) {
        it.json = JSON.parse(un(it.json));
        it.session = un(it.session);
        it.time = moment(it.time.$date).fromNow() + '\n' + moment(it.time.$date).format('MMMM Do YYYY, h:mm:ss a');
        it.$msg = un(it.msg);
        delete it.msg;
        return it;
      });
    });
  };

  adminotherCtrl = function($scope, $http) {};

  adminApp.controller("mainCtrl", mainCtrl);

  adminApp.controller("loginCtrl", loginCtrl);

  adminApp.controller("userCtrl", userCtrl);

  adminApp.controller("shopCtrl", shopCtrl);

  adminApp.controller("editshopCtrl", editshopCtrl);

  adminApp.controller("listOrderCtrl", listOrderCtrl);

  adminApp.controller("adminNavCtrl", adminNavCtrl);

  adminApp.controller("adminlogCtrl", adminlogCtrl);

  adminApp.controller("adminotherCtrl", adminotherCtrl);

  QINIU_BUCKET = 'anglestreet';

  qiniuimg = function() {
    return function(s, px, s3) {
      if (!s) {
        return "";
      }
      if (/^\d{0,3}$/.test(s)) {
        return '/static/images/type' + s + '.png';
      }
      if (/^http:\/\//.test(s)) {
        return s;
      }
      if (px) {
        return 'http://' + QINIU_BUCKET + '.qiniudn.com/' + s + '?imageView2/2/w/' + px + '/h/' + px + '';
      }
      return 'http://' + QINIU_BUCKET + '.qiniudn.com/' + s + '?imageView2/2/w/113/h/113';
    };
  };

  stringtojson = function() {
    return function(str) {
      return JSON.parse(str);
    };
  };

  indexApp.filter("qiniuimg", qiniuimg);

  adminApp.filter("qiniuimg", qiniuimg);

  adminApp.filter("stringtojson", stringtojson);

}).call(this);
