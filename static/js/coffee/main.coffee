# index

window.indexApp = angular.module("index", [
  # "ngSanitize"
  # "ngAnimate"
  "ngRoute"
  "ngCookies"
  # "infinite-scroll"
])

indexApp.config ($routeProvider, $locationProvider) ->
  $routeProvider.when("/",
    redirectTo:"/menu"
  ).when("/menu",
    templateUrl: "/static/template/menu.html"
  ).when("/shop",
    templateUrl: "/static/template/shoplist.html"
  ).when("/order/:id",
    templateUrl: "/static/template/order.html"
  ).when("/shop/:id",
    templateUrl:"/static/template/shop.html"
  ).when("/shop/:id/shopdetail",
    templateUrl:"/static/template/shopdetail.html"
  ).otherwise redirectTo: "/"
  # $locationProvider.html5Mode true


# shoplist.html
shopListCtrl = ($scope,$http)->
  window.w = $scope
  $http.get("/api/listshop",cache:true).success (data)->
    $scope.shopList=data
  return

# shop.html
shopCtrl = ($scope,$http,$routeParams,orderService,$location)->
  window.w = $scope
  $scope.order=orderService.readOrder()
  #shopid 
  $scope.id = $routeParams.id
  
  recalcuteOrder=->
    T=$scope.order
    #delete goods if number is 0
    _.each T.goods, (k,v)-> if k==0 then delete T.goods[v]
    [T.allcount,T.allprice] =_(T.goods).chain().pairs().reduce((s,n)->
        [ s[0]+n[1], s[1]+$scope.shopData.priceList[n[0]]*n[1] ]
      ,[0,0]).value()
    orderService.setOrder($scope.order)

  $http.get("/api/shop/"+$scope.id).success (data)->
    $scope.shopData=data
    #get goods classify
    $scope.category=_($scope.shopData.goods).chain().
      filter( (s)-> s.show ).
      pluck("category").groupBy().map( (n)->
        "name":n[0]
        "count":n.length
        ).sortBy((n)->-n.count).value()
    #make price table
    $scope.shopData.priceList={}
    for i in $scope.shopData.goods
      $scope.shopData.priceList[i.id]=parseInt(i.price)
    $scope.changeCategory("热卖")

  $scope.changeCategory=(name)->
    $scope.categoryNow=name
    T=_($scope.shopData.goods).chain()
    if name is "热卖"
      $scope.goods=T.sortBy((n)->-n.salesVolume).first(5).value()
    else if name is "我的订单"
      $scope.goods=T.filter((n)->$scope.order.goods[n.id]>0).sortBy((n)->-n.salesVolume).value()
    else 
      $scope.goods=T.filter((n)->~n.category.indexOf($scope.categoryNow)).sortBy((n)->-n.salesVolume).value()
    recalcuteOrder()

  $scope.clickAdd = (id,value)->
      unless $scope.order.goods[id]?
        $scope.order.goods[id]=0
      $scope.order.goods[id]+=value
      if $scope.order.goods[id]<0 then $scope.order.goods[id]=0
      recalcuteOrder()

  $scope.clickOrder=->
    orderService.setOrder($scope.order)
    if $scope.categoryNow != "我的订单"
      $scope.categoryNow = "我的订单"
      $scope.changeCategory("我的订单")
      return
    $location.path("/order/"+$routeParams.id)
  #shop goods img modal
  #todo  use ng-directives
  $scope.showModal =(img,name,price,salesVolume)->
    if img
      $scope.itemModal = {
        img
        name
        price
        salesVolume
      }
      $('#item_pic_m').modal('show')
  return

#order.html
orderCtrl = ($scope,$http,$routeParams,$location,orderService)->
  $scope.order=orderService.readOrder()

  #click return button to shop 
  $scope.clickReturn=->
    orderService.setOrder($scope.order)
    $location.path("/#/shop/"+$routeParams.id)

  $scope.clickOrderSubmit = ->
    orderService.setOrder($scope.order)
    order = orderService.readOrder()
    $scope.disable=true
    $http.post('/api/submitorder',order).success (data)->
      $scope.msg=data.msg
      $scope.disable=false
      unless data.error
        orderService.reset()
        $scope.order = orderService.readOrder()
    console.log order
  
  #save order info
  $scope.saveContent = ->
    orderService.setOrder($scope.order)

  return


orderService = ($http,$cookieStore,$routeParams) ->
  #order service

  _order=$cookieStore.get("order") ? {}

  do init = ->
    _.defaults _order,
      "goods":{}
      "allcount":0
      "allprice":0
      "name":""
      "tel":""
      "addr":""
      "msg":""
      "shopId":$routeParams.id

  @reset = ->
    _order = _.omit _order,['shopId','goods','allprice','allcount']
    init()
    $cookieStore.put("order",_order)
    
  @setOrder = (order)->
    _order=order
    $cookieStore.put("order",_order)

  @readOrder = ->
    if $routeParams.id != _order.shopId
      _order = _.omit _order,['shopId','goods','allprice','allcount']
      init()
      $cookieStore.put("order",_order)
    _order

  @addInf = (name,tel,addr)->
    _order.name=name
    _order.tel=tel
    _order.addr=addr
    $cookieStore.put("order",_order)
  return

indexApp.controller "shopCtrl", shopCtrl
indexApp.controller "shopListCtrl", shopListCtrl
indexApp.service "orderService",orderService
indexApp.controller "orderCtrl", orderCtrl


#admin
 
window.adminApp = angular.module("admin", [
  # "ngSanitize"
  "ngAnimate"
  "ngRoute"
  "ngCookies"
  "ngToast"
  # "infinite-scroll"
  # "angularFileUpload"
])

adminApp.config ($routeProvider, $locationProvider) ->
  $routeProvider.when("/admin",
    templateUrl: "/static/admintemplate/adminmain.html"
  ).when("/admin/login",
    templateUrl:"/static/admintemplate/adminlogin.html"
  ).when("/admin/listuser",
    templateUrl:"/static/admintemplate/adminlistuser.html"
  ).when("/admin/listshop",
    templateUrl:"/static/admintemplate/adminlistshop.html"
  ).when("/admin/listorder",
    templateUrl:"/static/admintemplate/adminlistorder.html"
  ).when("/admin/editshop/:id",
    templateUrl:"/static/admintemplate/admineditshop.html"
  ).when("/admin/log",
    templateUrl:"/static/admintemplate/adminlog.html"
  ).when("/admin/other",
    templateUrl:"/static/admintemplate/adminother.html"
  ).otherwise redirectTo: "/admin"
  $locationProvider.html5Mode true

`

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

`

#adminmain.html
mainCtrl = ($scope,$http,$interval,$location,ngToast)->
  if $scope.login.isLogin == false
      $location.path("/admin/login")
      ngToast.create('你没有登陆或者已经登陆超时,请成功登陆');

  $scope.logout = ->
    $http.get('/api/logout').success (data)->
      if data.error==false
        $scope.updateLoginState()
        $location.path("/admin/login")
        ngToast.create('退出登陆成功');

#admin.html
adminNavCtrl = ($scope,$http,$interval,$location,ngToast)->
  $scope.login={}
  $scope.updateLoginState = (showmsg=false)->
    $http.get('/api/islogin').success (data)->
      if data.error
        $location.path("/admin/login")
        $scope.login.isLogin=false
        if showmsg then ngToast.create('你还没有登陆')
      else 
        $scope.username=data.username
        $scope.login.isLogin=true
        if showmsg then ngToast.create('欢迎登陆,'+data.username)
        if $location.url()=='/admin/login'
          $location.path("/admin")

  $interval $scope.updateLoginState(false),1000 * 60
  do $scope.updateLoginState


loginCtrl =  ($scope,$http,$interval,$location,ngToast)->
  $scope.username=""
  $scope.passwd=""

  $scope.login = ->
    p = {username:$scope.username,passwd:$scope.passwd}
    $http.post('/api/login',p).success (data)->
      console.log  data
      if data.error
        ngToast.create(content:data.msg,class:"danger")
      else
        ngToast.create('登陆成功');
        $scope.updateLoginState(false)

#adminlistuser.html
userCtrl = ($scope,$http,$interval,$location,ngToast)->
  $scope.updateLoginState(false)
  $scope.msg=""
  $scope.state="add"
  do $scope.clear = ->
    $scope.usernow = 
      username:""
      passwd:""
      comment:""
      role:""
      tel:""
      qq:""
  $scope.clear()
  do init = ->
    $http.get('/api/admin/listuser').success (data)->
      if data.error
        if data.msg=="没有权限"
          $scope.updateLoginState(true)
        return 
      $scope.users =data
  
  $scope.choose = (user)->
    $scope.usernow = _.clone user
    $scope.state ='edit'

  $scope.add = ->
    if $scope.state is 'add'
      $http.post('/api/admin/adduser',$scope.usernow).success (data)->
        $scope.msg=data.msg
        ngToast.create data.msg
        do init
    else
      $scope.clear()
      $scope.state='add'

  $scope.update = ->
    $http.post('/api/admin/updateuser',$scope.usernow).success (data)->
      $scope.msg=data.msg
      ngToast.create data.msg
    do init      

  $scope.del = ->
    $http.post('/api/admin/deluser',$scope.usernow).success (data)->
      $scope.msg=data.msg
      ngToast.create data.msg
      do init


shopCtrl = ($scope,$http,$interval,$location,fileUpload,$timeout,ngToast)->
  $scope.updateLoginState()
  window.w = $scope
  $scope.state="new"
  $scope.upload = ->
    file = $scope.myFile
    unless file 
      ngToast.create "没有选择文件"
      return 
    uploadUrl = "/api/admin/upload"
    fileUpload.uploadFileToUrl file, uploadUrl,(data)->
      if data.$error
        ngToast.create data.msg
      ngToast.create "文件上传成功"
      $scope.shopnow.info.shopImg=data.url
    return
  do $scope.clear = ->
    $scope.shopnow=
      info:
        name: ""
        tel:""
        city: ""
        shopImg: "1"
        deliveryTime: "30"
        freePrice: ""
        area: ""
        addPrice: "10"
        state: "营业"
        startPrice: "12"
        msg: ""
        desc: ""
        shortName:""
        addr: "湘潭市"
        weixin:""
      data:
        show: true
        admin: ""
        star: "5"
        proority: "0"
      goods:[]
      shopImg:"1"

  do init = ->
    # api data:admin key should a string not a array
    $http.get('/api/admin/listshop').success (data)->
      console.log data
      if data.error
        if data.msg=="没有权限"
          $scope.updateLoginState(true)
        return
      $scope.shops = data

  $scope.add = ->
    if $scope.state is "edit"
      $scope.clear()
      $scope.state="new"
      return
    if $scope.state is "new"
      console.log 'add shop',$scope.shopnow
      $http.post('/api/admin/addshop',$scope.shopnow).success (data)->
        console.log data
        ngToast.create data.msg
        do init

  $scope.del = ->
    $http.post('/api/admin/delshop',$scope.shopnow).success (data)->
      console.log data
      ngToast.create data.msg

  $scope.choose = (shop)->
    $scope.state="edit"
    $scope.shopnow=shop
    $scope.shopnow.id = shop._id.$oid

  $scope.update = ->
    if $scope.state is "new"
      ngToast.create "选择店铺之后才能更新哦"
      return
    $http.post('/api/admin/updateshop',$scope.shopnow).success (data)->
      console.log data
      $scope.shops = data
      ngToast.create data.msg
      do init

  $scope.completionWeixin = ->
    w = $scope.shopnow.info.weixin
    if not w then return
    $http.get('/api/admin/filteropenid/'+w).success (data)->
      if data.length > w.length
        $scope.shopnow.info.weixin = data

editshopCtrl = ($scope,$http,$interval,$location,$routeParams,$timeout,fileUpload,ngToast)->
  window.w=$scope
  $scope.state="new"

  do $scope.clear = ->
    $scope.good=
      id: _.max(_($scope.shop?.goods).pluck('id'))+1
      name: ""
      category: ""
      img: ""
      show:true
      price: 10.0
      salesVolume:0
      point: 0
      desc: ""
    $scope.now='add'

  $scope.upload = ->
    file = $scope.myFile
    console.log "file is " + JSON.stringify(file)
    uploadUrl = "/api/admin/upload"
    fileUpload.uploadFileToUrl file, uploadUrl,(data)->
      console.log data
      $scope.good.img=data.url
    return

  $scope.add = ->
    if $scope.state is "edit"
      $scope.clear()
      $scope.state="new"
      return
    if $scope.shopform.$valid
      console.log 'add good',$scope.good
      $scope.shop.goods.push($scope.good)
      $scope.clear()
      ngToast.create "成功新增,你必须按保存键才能生效"
    else 
      ngToast.create "你的填写不完全,添加失败"

  $scope.choose = (shop)->
    $scope.state="edit"
    $scope.good=shop

  $scope.del = ()->
    if $scope.state is "new"
      return
    for good,index in $scope.shop.goods
      if good==$scope.good
        $scope.shop.goods.splice(index,1)
        ngToast.create "成功删除,你必须按保存键才能生效"
        return

  $scope.save = ->
    $scope.shop.id=$routeParams.id
    $http.post('/api/admin/updateshopgoods',$scope.shop).success (data)->
      console.log data
      ngToast.create data.msg
      do init

  do init = ->
    console.log  $scope.id = $routeParams.id
    $http.get('/api/admin/shopinfo/'+$scope.id).success (data)->
      if data.error
        if data.msg=="没有权限"
          $scope.updateLoginState true
          return
        ngToast data.msg
      console.log data
      $scope.shop=data
      $scope.clear()


listOrderCtrl = ($scope,$http,$interval,$location,$routeParams,fileUpload,ngToast)->
  window.jQuery ->  
    $('.tips').tooltip('hide')
  $scope.updateLoginState()
  window.w = $scope
  $scope.state="all"
  $scope.page = 0
  $scope.chooseState = (state)->
    $scope.state = state
    $scope.page = 0 
    $scope.reload()

  $scope.lastpage = ->
    if $scope.page>0 
      $scope.page--
      $scope.reload()
  $scope.nextpage = ->
    $scope.page++
    $scope.reload()

  do $scope.reload = ->
    $http.get('/api/admin/listorder/'+$scope.state+'/'+$scope.page).success (data)->
      if data.length==0 and $scope.page>0 
        ngToast.create "没有这一页了。"
        $scope.page--
        return
      $scope.orderlist = data
      $scope.orderNow = $scope.orderlist[0]
  $scope.choose = (item)->
    $scope.orderNow = item

  $scope.sendCmd = (cmd)->
    data = {
      cmd:cmd
      id:$scope.orderNow._id.$oid
    }
    $http.post('/api/admin/ordercmd',data).success (data)->
      if data.error 
        ngToast.create class:"error" ,data.msg
      else 
        ngToast.create data.msg
      $scope.reload()
      
  $scope.orderModifyState = (state)->
    data = {
      state:state
      id:$scope.orderNow._id.$oid
    }
    $http.post('/api/admin/ordermodifystate',data).success (data)->
      ngToast.create data.msg
      $scope.reload()

adminlogCtrl = ($scope,$http)->
  un = (s)-> unescape(s.replace(/\\/g, "%"))
  $http.get('/api/admin/log/0').success (data)->
    $scope.log = _(data).map (it)->
      it.json = JSON.parse(un(it.json))
      it.session = un(it.session)
      it.time = moment(it.time.$date).fromNow() + '\n' + moment(it.time.$date).format('MMMM Do YYYY, h:mm:ss a')
      it.$msg = un(it.msg)
      delete it.msg
      return it

adminotherCtrl = ($scope,$http)->

adminApp.controller "mainCtrl",mainCtrl
adminApp.controller "loginCtrl",loginCtrl
adminApp.controller "userCtrl",userCtrl
adminApp.controller "shopCtrl",shopCtrl
adminApp.controller "editshopCtrl",editshopCtrl
adminApp.controller "listOrderCtrl",listOrderCtrl
adminApp.controller "adminNavCtrl",adminNavCtrl
adminApp.controller "adminlogCtrl",adminlogCtrl
adminApp.controller "adminotherCtrl",adminotherCtrl


#common

# filter
QINIU_BUCKET = 'anglestreet'
qiniuimg = ->
  (s,px,s3)->
    if not s then return ""
    if /^\d{0,3}$/.test(s)
      return '/static/images/type'+s+'.png'
    if /^http:\/\//.test(s)
      return s
    if px
      return 'http://'+QINIU_BUCKET+'.qiniudn.com/'+s+'?imageView2/2/w/'+px+'/h/'+px+''
    return 'http://'+QINIU_BUCKET+'.qiniudn.com/'+s+'?imageView2/2/w/113/h/113'


stringtojson = ->
  (str)->
    return JSON.parse(str)


indexApp.filter "qiniuimg", qiniuimg
adminApp.filter "qiniuimg", qiniuimg
adminApp.filter "stringtojson", stringtojson

