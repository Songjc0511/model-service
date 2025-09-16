#!/usr/bin/env python3
"""
查看对话历史记录的脚本
"""
import requests
import json
from datetime import datetime

def view_user_conversations(user_id):
    """查看用户的所有对话"""
    print(f"=== 用户 {user_id} 的对话列表 ===")
    
    headers = {"X-User-ID": user_id}
    
    try:
        # 获取对话列表
        response = requests.get("http://localhost:8000/api/v1/conversations", headers=headers)
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"找到 {len(conversations)} 个对话:")
            
            for i, conv in enumerate(conversations, 1):
                print(f"\n{i}. 对话ID: {conv['id']}")
                print(f"   标题: {conv['title']}")
                print(f"   创建时间: {conv['created_at']}")
                print(f"   更新时间: {conv['updated_at']}")
                print(f"   状态: {'活跃' if conv['is_active'] else '已关闭'}")
            
            return conversations
        else:
            print(f"❌ 获取对话列表失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def view_conversation_messages(user_id, conversation_id):
    """查看特定对话的消息历史"""
    print(f"\n=== 对话 {conversation_id} 的消息历史 ===")
    
    headers = {"X-User-ID": user_id}
    
    try:
        # 获取消息历史
        response = requests.get(
            f"http://localhost:8000/api/v1/conversations/{conversation_id}/messages",
            headers=headers
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"找到 {len(messages)} 条消息:")
            
            for i, msg in enumerate(messages, 1):
                print(f"\n{i}. 消息ID: {msg['id']}")
                print(f"   类型: {msg['message_type']}")
                print(f"   内容: {msg['content']}")
                print(f"   时间: {msg['timestamp']}")
                print(f"   发送者: {'用户' if msg['is_user_message'] else '系统'}")
            
            return messages
        else:
            print(f"❌ 获取消息历史失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def view_user_stats(user_id):
    """查看用户统计信息"""
    print(f"\n=== 用户 {user_id} 的统计信息 ===")
    
    headers = {"X-User-ID": user_id}
    
    try:
        # 获取用户统计
        response = requests.get("http://localhost:8000/api/v1/users/me/stats", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"总对话数: {stats['total_conversations']}")
            print(f"总消息数: {stats['total_messages']}")
            print(f"平均响应频率: {stats['avg_response_frequency']}")
            print(f"最后活跃时间: {stats['last_active']}")
            print(f"创建时间: {stats['created_at']}")
        else:
            print(f"❌ 获取用户统计失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def main():
    """主函数"""
    print("对话历史查看工具")
    print("=" * 50)
    
    # 设置用户ID
    user_id = input("请输入用户ID (直接回车使用默认值 'test_user'): ").strip()
    if not user_id:
        user_id = "test_user"
    
    print(f"\n正在查看用户 {user_id} 的历史记录...")
    
    # 查看用户统计
    view_user_stats(user_id)
    
    # 查看对话列表
    conversations = view_user_conversations(user_id)
    
    if conversations:
        # 让用户选择查看哪个对话的详细消息
        try:
            choice = input(f"\n请选择要查看的对话 (1-{len(conversations)}, 直接回车查看第一个): ").strip()
            
            if not choice:
                choice = 1
            else:
                choice = int(choice)
            
            if 1 <= choice <= len(conversations):
                selected_conv = conversations[choice - 1]
                view_conversation_messages(user_id, selected_conv['id'])
            else:
                print("❌ 无效的选择")
                
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n操作被取消")
    else:
        print("没有找到对话记录")

if __name__ == "__main__":
    main()
