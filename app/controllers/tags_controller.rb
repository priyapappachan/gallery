class TagsController < ApplicationController
 def create
    @resource = Resource.find(params[:resource_id])
    @tag = @resource.tags.create(tag_params)
    redirect_to resource_path(@resource)
 end

  def new
    @tag = Tag.new
  end

 def tagged
  if params[:tag].present? 
    @resources = Resource.tagged_with(params[:tag])
  else 
    @resources = Resource.resourceall
  end  
 end

 def index
    if params[:tag]
     @resources = Resource.tagged_with(params[:tag])
    else
     @resources = Resource.all
    end
 end

  private
    def tag_params
      params.require(:resource).permit(:tag_list, :name)
  end
end
