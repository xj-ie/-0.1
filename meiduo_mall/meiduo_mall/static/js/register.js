let vm = new Vue({
                el: "#app",
//                delimiters:['[[","]]'],
                delimiters: ['[[', ']]'],
                data:{
    //                    v-model
                        username:"",
                        password:"",
                        password2:"",
                        mobile:"",
                        allow:"",
                        uuid:"",
                        img_db:"",

    //                    error_message
                        error_name_message:"",
                        error_pass_message:"",
                        error_phone_massage:"",
    //                    v-show
                        error_name:false,
                        error_pass:false,
                        error_pass2:false,
                        error_phone:false,
                        error_allow:false,
                        error_img:false,


                    },
                mounted(){
                            this.img_show();
                        },
                methods:{
                            img_show(){
                                        let code_img = generateUUID();
                                        this.uuid = "/image_code/"+ code_img +"/";
                                      },
                            check_img(){
                                       },
                            check_username(){
//                            username : len{5:20} range[0-9A-Za-z_-]

                                            let re = /^[0-9A-Za-z_-]{5,20}$/;
                                            if (re.test(this.username)){
                                                                            this.error_name = false;
//                                                                            this.error_name_message = "unique user register"
                                                                        }
                                            else{
                                                    this.error_name_message = "no suitable type len ?";
                                                    this.error_name = true;

                                                }
                                            if (this.error_name==false){
                                                                            let url = "user/" + this.username + "/conuter"
                                                                            axios.get(url, {"responseType": "json"})
                                                                            .then(response=>{

                                                                                                if(response.data.conut==1){
                                                                                                                            this.error_name_message = "user_name unique!";
                                                                                                                            this.error_name = true;
                                                                                                                          }
                                                                                                else{
                                                                                                        this.error_name=this.error_name;
                                                                                                    }

                                                                                            })
                                                                            .catch(error=>{
                                                                                            console.log(error.response);

                                                                                           })
                                                                       }


                                            },
                            check_password(){
                                                let re = /^[0-9A-Za-z]{8,12}$/
                                                if (re.test(this.password)){
                                                                                this.error_pass =false;
                                                                            }
                                                else{
                                                        this.error_pass_message = "no suitable type len !"
                                                        this.error_pass = true;
                                                    }

                                            },
                            check_password2(){
                                                if (this.password===this.password2){
                                                                                        this.error_pass2=false;
                                                                                    }
                                                else{
                                                      this.error_pass2=true;
                                                    }

                                            },
                            check_mobile(){
                                                let re = /^1[3-9]\d{9}$/
                                                if (re.test(this.mobile)){
                                                                            this.error_phone=false;
                                                                        }
                                                else{
                                                        this.error_phone_massage = "phone format len error　！";
                                                        this.error_phone = true;
                                                    }
                                                if (this.error_phone==false){
                                                                                let ual = "phone/" + this.mobile + "/counter";
                                                                                axios.get(ual, {"responseType": "json"})
                                                                                .then(response=>{
                                                                                                    if (response.data.conut==1){
                                                                                                                                            this.error_phone_massage = "phone_dtype: NOT PHONE　unique!!";
                                                                                                                                            this.error_phone=true;
                                                                                                                                }
                                                                                                    else{
                                                                                                            this.error_phone = this.error_phone;
                                                                                                        }

                                                                                                })
                                                                                .catch(error=>{
                                                                                              console.log(error.response);
                                                                                              })
                                                                            }

                                            },
                            check_allow(){
                                            if (this.allow){
                                                                this.error_allow = false;
                                                            }
                                            else{
                                                    this.error_allow = true;
                                                }

                                           },
                            on_submit(){
                                            this.check_username();
                                            this.check_password();
                                            this.check_password2();
                                            this.check_mobile();
                                            this.check_allow();
                                            if (this.error_username==true || this.error_pass==true || this.error_pass2==true || this.error_phone==true || this.error_allow==true){
                                                                                                                                                        window.event.returnValue = false;
                                                                                                                                                    }
//                                            else{
//    //                                                    window.event.returnValue =false;
//                                                    alter("commit TRUE");
//                                                }



                                        },
                        },

                })