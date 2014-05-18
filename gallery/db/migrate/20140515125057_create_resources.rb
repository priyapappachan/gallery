class CreateResources < ActiveRecord::Migration
  def change
    create_table :resources do |t|
     # t.string :tag_list
      t.timestamps
    end
  end
end
