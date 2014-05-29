class CommentsController < ApplicationController
  def create
    @resource = Resource.find(params[:resource_id])
    @comment = @resource.comments.create(comment_params)
    redirect_to resource_path(@resource)
  end
 
  private
    def comment_params
      params.require(:comment).permit(:body)
    end
end
