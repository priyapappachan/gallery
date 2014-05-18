class ResourcesController < ApplicationController
  before_action :set_resource, only: [:show, :edit, :update, :destroy]

  
  def index
    if params[:tag]
     @resources = Resource.tagged_with(params[:tag])
    else
     @resources = Resource.all
    end    
  end

  def show
	@resource = Resource.find(params[:id])
  end

  # GET /resources/new
  def new
    @resource = Resource.new
  end

  # GET /resources/1/edit
  def edit
  end

  def create
    @resource = Resource.new(resource_params)
    
    if @resource.save
	redirect_to @resource
    else
 	render 'new'
    end
    
  end

#for tags
 def tagged
  if params[:tag].present? 
    @resources = Resource.tagged_with(params[:tag])
  else 
    @resources = Resource.resourceall
  end  
 end

  # PATCH/PUT /resources/1
  # PATCH/PUT /resources/1.json
  def update
    respond_to do |format|
      if @resource.update(resource_params)
        format.html { redirect_to @resource, notice: 'Resource was successfully updated.' }
        format.json { render :show, status: :ok, location: @resource }
      else
        format.html { render :edit }
        format.json { render json: @resource.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /resources/1
  def destroy
    @resource.destroy
    respond_to do |format|
      format.html { redirect_to resources_url, notice: 'Resource was successfully destroyed.' }
      format.json { head :no_content }
    end
  end

  private
    def set_resource
      @resource = Resource.find(params[:id])
    end

    def resource_params
      params.require(:resource).permit(:tag_list,:pic,:name)
    end
end
