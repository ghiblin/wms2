Backbone.Singleton = {
  getInstance:function(){
    if( this._instance == undefined ){
      this._instance = new this();
    }
    return this._instance;
  },
  setInstance:function(inst){
    this._instance = inst;
  }
}